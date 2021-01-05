# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    batch_id = fields.Many2one('op.batch', string='Preferred batch')
    code_product_rel = fields.Char(related='batch_id.course_id.code')
    product_id_default_code = fields.Char(related='product_id.default_code')
    campus_id_code = fields.Char(related='order_id.team_id.campus_id.code')

    @api.onchange
    def onchange_batch(self):
        campus_code = self.order_id.team_id.campus_id.code
        return {'domain': {
            'batch_id': [('course_id.code', '=', self.product_id.default_code),
                         ('end_date', '>', datetime.datetime.today()),
                         ('code', 'ilike', campus_code)]}}
