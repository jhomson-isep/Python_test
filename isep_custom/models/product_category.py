# -*- coding: utf-8 -*-

from openerp import api, fields, models


class product_category(models.Model):
    _inherit = 'product.category'
    x_compania = fields.Selection([('ISEP', 'ISEP'), ('ISED', 'ISED')], string="ISEP/ISED")
    x_codigocategoria = fields.Char(string="Código")