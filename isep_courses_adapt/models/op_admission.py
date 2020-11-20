# -*- coding: utf-8 -*-

from odoo import models, fields


class OpAdmission(models.Model):
    _inherit = 'op.admission'
    sale_order_id = fields.Integer(string='Sale Order')
