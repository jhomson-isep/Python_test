# -*- coding: utf-8 -*-

from openerp import api, fields, models


class x_crmtipodecurso(models.Model):
    _name = 'x.crmtipodecurso'

    x_codigotipodecurso = fields.Char(string="Código")
    x_matricula = fields.Float(string="Matrícula")
    x_name = fields.Char(string="Nombre")
