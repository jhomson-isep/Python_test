# -*- coding: utf-8 -*-

from openerp import api, fields, models


class x_crm_horariosdecontacto(models.Model):
    _name = 'x.crm.horariosdecontacto'

    x_name = fields.Char(string="Horario de contacto")
