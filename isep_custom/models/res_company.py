# -*- coding: utf-8 -*-


from openerp import api, fields, models


class product_template(models.Model):
    _inherit = 'product.template'
    x_Identidad = fields.Integer(string="Identidad")
