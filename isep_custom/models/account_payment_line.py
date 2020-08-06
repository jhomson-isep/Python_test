# -*- coding: utf-8 -*-

from openerp import fields, models


class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'

    partner_country_id = fields.Char(
        string="Pais",
        related="partner_id.country_id.name")
