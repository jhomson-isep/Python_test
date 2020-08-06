# -*- coding: utf-8 -*-


from openerp import api, fields, models


class product_template(models.Model):
    _inherit = 'product.template'
    x_tipodecurso = fields.Many2one('x.crmtipodecurso', string="Tipo de Curso")
    #  tipodecurso se rellena con los updates del hooks.
    tipodecurso = fields.Selection([
                                    ('curso', 'Curso'),
                                    ('mat', 'Matrícula'),
                                    ('rec', 'Recargo'),
                                    ('desc', 'Descuento'),
                                    ('desc_ma', 'Descuento Matrícula'),
                                    ('inc', 'Incremento'),
                                    ('pgrado', 'Posgrado'),
                                    ('diplo', 'Diplomado'),
                                    ('master', 'Master'),
                                    ('mgrafico', 'Monográfico'),
                                    ('gasto_env', 'Gastos de envio'),
                                    ], string="Tipo de curso", default="curso")
