from datetime import date
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
import base64
from collections import OrderedDict
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.tools import image_resize_image
# from odoo.addons.portal.controllers.portal import CustomerPortal, \
#     pager as portal_pager, get_records_pager
from odoo.addons.portal.controllers.portal import pager as portal_pager, \
    get_records_pager
from odoo.addons.purchase.controllers.portal import CustomerPortal
from odoo.addons.web.controllers.main import Binary
from odoo.osv import expression
import logging

logger = logging.getLogger(__name__)


class CustomerPurchasePortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPurchasePortal, self)._prepare_portal_layout_values()
        values['purchase_count'] = request.env['purchase.order'].search_count([
            ('state', 'in', ['sent', 'purchase', 'done', 'cancel'])
        ])
        return values

    @http.route(['/my/purchase', '/my/purchase/page/<int:page>'], type='http',
                auth="user", website=True)
    def portal_my_purchase_orders(self, page=1, date_begin=None, date_end=None,
                                  sortby=None, filterby=None, **kw):
        res = super(CustomerPurchasePortal, self).portal_my_purchase_orders(
            page, date_begin, date_end, sortby, filterby, **kw)
        values = self._prepare_portal_layout_values()

        domain = []

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [
                ('state', 'in', ['sent', 'purchase', 'done', 'cancel'])]},
            'purchase': {'label': _('Purchase Order'),
                         'domain': [('state', '=', 'purchase')]},
            'cancel': {'label': _('Cancelled'),
                       'domain': [('state', '=', 'cancel')]},
            'done': {'label': _('Locked'), 'domain': [('state', '=', 'done')]},
        }
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        values.update({
            'date': date_begin,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(
                sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/purchase',
        })
        return res

    @http.route(['/my/purchase/<int:order_id>/accept'], type='json',
                auth="public", website=True)
    def portal_purchase_accept(self, res_id, access_token=None,
                               partner_name=None,
                               signature=None, order_id=None):
        logger.info("**** on accept ***")
        logger.info("res_id: {0}".format(res_id))
        try:
            order_sudo = self._document_check_access('purchase.order', res_id,
                                                     access_token=access_token)
            logger.info(order_sudo.get_portal_url(
                query_string='&message=sign_ok'))
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
