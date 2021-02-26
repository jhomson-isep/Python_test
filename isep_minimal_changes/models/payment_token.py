# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


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

    @api.model
    def create(self, token):

        date = token.get('caducidad')
        date = datetime.strptime(date, '%Y-%m-%d')
        #years on days 'cause the timedelta function do not have years attribute
        years = 730485
        if date.year < 2000:
            date = date + timedelta(days=years)
            token.update({'caducidad': date})
        res = super(PaymentToken, self).create(token)
        return res
