from datetime import date
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from collections import OrderedDict
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
import logging

logger = logging.getLogger(__name__)


class CustomerPurchasePortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPurchasePortal,
                       self)._prepare_portal_layout_values()
        values['purchase_count'] = request.env['purchase.order'].search_count([
            ('state', 'in', ['sent', 'purchase', 'done', 'cancel'])
        ])
        values['searchbar_filters'] = {
            'all': {'label': _('All'), 'domain': [
                ('state', 'in', ['sent', 'purchase', 'done', 'cancel'])]},
            'purchase': {'label': _('Purchase Order'),
                         'domain': [('state', '=', 'purchase')]},
            'cancel': {'label': _('Cancelled'),
                       'domain': [('state', '=', 'cancel')]},
            'done': {'label': _('Locked'), 'domain': [('state', '=', 'done')]},
        }
        logger.info("values: {0}".format(values))
        return values

    @http.route(['/my/purchase', '/my/purchase/page/<int:page>'], type='http',
                auth="user", website=True)
    def portal_my_purchase_orders(self, page=1, date_begin=None, date_end=None,
                                  sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        PurchaseOrder = request.env['purchase.order']

        domain = []

        archive_groups = self._get_archive_groups('purchase.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'date': {'label': _('Newest'),
                     'order': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
            'amount_total': {'label': _('Total'),
                             'order': 'amount_total desc, id desc'},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [
                ('state', 'in', ['sent', 'purchase', 'done', 'cancel'])]},
            'purchase': {'label': _('Purchase Order'),
                         'domain': [('state', '=', 'purchase')]},
            'cancel': {'label': _('Cancelled'),
                       'domain': [('state', '=', 'cancel')]},
            'done': {'label': _('Locked'), 'domain': [('state', '=', 'done')]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # count for pager
        purchase_count = PurchaseOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/purchase",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=purchase_count,
            page=page,
            step=self._items_per_page
        )
        # search the purchase orders to display, according to the pager data
        orders = PurchaseOrder.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_purchases_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'orders': orders,
            'page_name': 'purchase',
            'pager': pager,
            'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(
                sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/purchase',
        })
        return request.render("purchase.portal_my_purchase_orders", values)

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
