# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    batch_id = fields.Many2one('op.batch', string='Preferred batch')
    code_product_rel = fields.Char(related='batch_id.course_id.code')
    product_id_default_code = fields.Char(related='product_id.default_code')

    @api.onchange('product_id')
    def onchange_batch(self):
        return {'domain': {
            'batch_id': [('course_id.code', '=', self.product_id.default_code),
                         ('end_date', '>', datetime.datetime.today())]}}
