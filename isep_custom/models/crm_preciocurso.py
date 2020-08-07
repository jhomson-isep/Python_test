# -*- coding: utf-8 -*-

from openerp import api, fields, models


class x_crm_preciodecurso(models.Model):
    _name = 'x.crm.preciodecurso'

    x_company_id = fields.Many2one('res.company', string="Compañía")
    x_modalidad_id = fields.Many2one('product.attribute.value', string="Modalidad")
    x_precio = fields.Float(string="Precio")
    x_prod_id = fields.Many2one('product.template', string="Curso")
    x_sede_id = fields.Many2one('product.attribute.value', string="Sede")