# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging

logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    require_signature = fields.Boolean('Online Signature', default=True,
                                       readonly=True,
                                       states={'draft': [('readonly', False)],
                                               'sent': [('readonly', False)]},
                                       help='Request a online signature to '
                                            'the customer in order to confirm '
                                            'orders automatically.')
    signature = fields.Binary('Signature',
                              help='Signature received through the portal.',
                              copy=False, attachment=True)
    signed_by = fields.Char('Signed by',
                            help='Name of the person that signed the SO.',
                            copy=False)
    has_invoice_attached = fields.Boolean('Has attachments', default=False,
                                          compute='_set_has_invoice_attached',
                                          search='_attached_search',
                                          stored=True)

    def has_to_be_signed(self, also_in_draft=False):
        return (self.state == 'sent' or (
                self.state == 'draft' and also_in_draft)) and self.require_signature and not self.signature

    def has_attachments(self):
        attachments = self.env['ir.attachment'].search_count([(
            'res_model', '=', self._name), ('res_id', '=', self.id)])
        if attachments > 0:
            self.has_invoice_attached = True
        return attachments

    def _set_has_invoice_attached(self):
        for order in self:
            attachments = self.env['ir.attachment'].search_count([(
                'res_model', '=', order._name), ('res_id', '=', order.id)])
            logger.debug(attachments)
            if attachments > 0:
                order.has_invoice_attached = True

    @api.multi
    def _attached_search(self, operator, value):
        recs = self.search([]).filtered(
            lambda x: x.has_invoice_attached is True)
        if recs:
            return [('id', 'in', [x.id for x in recs])]

    def action_create_purchase_invoice(self):
        invoice = self.env['account.invoice'].create({
            'type': 'in_invoice',
            'purchase_id': self.id,
            'partner_id': self.partner_id.id,
        })
        invoice.purchase_order_change()
        invoice.action_invoice_open()
