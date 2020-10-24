# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'account.invoice'

    active = fields.Boolean(string='active', default=True)