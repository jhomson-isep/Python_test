# -*- coding: utf-8 -*-


from openerp import api, fields, models


class product_template(models.Model):
    _inherit = 'product.template'
    x_tipodecurso = fields.Many2one('x.crmtipodecurso', string="Tipo de Curso")
    alias = fields.Char(string="Alias")