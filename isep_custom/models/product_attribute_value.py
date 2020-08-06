# -*- coding: utf-8 -*-

from openerp import api, fields, models


class product_attribute_value(models.Model):
    _inherit = 'product.attribute.value'

    x_activo = fields.Boolean(string="Activo")
    x_descripcion = fields.Char(string="Descripción")
