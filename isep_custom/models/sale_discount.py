# -*- coding: utf-8 -*-

from openerp import api, fields, models


class x_sale_discount(models.Model):
    _name = 'x.sale.discount'

    x_activo = fields.Boolean(string="Activo")
    x_value = fields.Integer(string="Valor")
