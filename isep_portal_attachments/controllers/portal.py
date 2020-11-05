from datetime import date
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, \
    pager as portal_pager, get_records_pager
from odoo.osv import expression


class CustomerPortal(CustomerPortal):

    @http.route(['/my/purchase/<int:order_id>/accept'], type='json',
                auth="public", website=True)
    def portal_quote_accept(self, res_id, access_token=None, partner_name=None,
                            signature=None, order_id=None):
        try:
            order_sudo = self._document_check_access('purchase.order', res_id,
                                                     access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order')}

        if not order_sudo.has_to_be_signed():
            return {'error': _(
                'Order is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        order_sudo.signature = signature
        order_sudo.signed_by = partner_name

        # pdf = request.env.ref('sale.action_report_saleorder').sudo().render_qweb_pdf(
        #     [order_sudo.id])[0]
        # _message_post_helper(
        #     res_model='sale.order',
        #     res_id=order_sudo.id,
        #     message=_('Order signed by %s') % (partner_name,),
        #     attachments=[('%s.pdf' % order_sudo.name, pdf)],
        #     **({'token': access_token} if access_token else {}))

        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(
                query_string='&message=sign_ok'),
        }

    @http.route(['/my/purchase/<int:order_id>/decline'], type='http',
                auth="public", methods=['POST'], website=True)
    def decline(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('purchase.order',
                                                     order_id,
                                                     access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message = post.get('decline_message')

        query_string = False
        if order_sudo.has_to_be_signed() and message:
            order_sudo.action_cancel()
            _message_post_helper(message=message, res_id=order_id,
                                 res_model='purchase.order', **{
                    'token': access_token} if access_token else {})
        else:
            query_string = "&message=cant_reject"

        return request.redirect(
            order_sudo.get_portal_url(query_string=query_string))
