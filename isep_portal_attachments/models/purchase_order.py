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
        self.env.user.company_id = self.company_id
        self.env['ir.default'].clear_caches()
        invoice_sudo = self.env['account.invoice'].sudo()
        partner_bank_ids = self.partner_id.bank_ids
        payment_mode = self.partner_id.supplier_payment_mode_id
        if len(payment_mode) < 1:
            payment_mode = self.env['account.payment.mode'].search(
                [('payment_type', '=', 'outbound'),
                 ('company_id', '=', self.company_id.id),
                 ('name', 'ilike', 'profesor')])
        payment_term = self.partner_id.property_supplier_payment_term_id
        if len(payment_term) < 1:
            payment_term = self.env['account.payment.term'].search(
                [('company_id', '=', self.company_id.id),
                 ('name', 'ilike', '2 Meses dia 25')])
        invoice = invoice_sudo.create({
            'type': 'in_invoice',
            'purchase_id': self.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': partner_bank_ids[0].id if len(
                partner_bank_ids) > 0 else None,
        })
        invoice.purchase_order_change()
        invoice.write({'payment_mode_id': payment_mode.id,
                       'payment_term_id': payment_term.id})
        invoice.compute_taxes()
        invoice.amount_tax = sum(line.amount for line in invoice.tax_line_ids)
        invoice.action_invoice_open()

    @api.multi
    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % ('Solicitud de presupuesto', self.name)
