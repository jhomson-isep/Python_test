# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'res.country'

    active = fields.Boolean(string='active', default=True)
