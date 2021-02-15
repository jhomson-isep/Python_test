# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    masked_card_number = fields.Char(string="Masked card number",
                                     compute='_compute_card_number')

    @api.multi
    def _compute_card_number(self):
        for card in self:
            if card.acquirer_ref:
                card.masked_card_number = ' '.join(['**** **** ****',
                                                    card.acquirer_ref[-4:]])
