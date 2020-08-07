# -*- coding: utf-8 -*-

from openerp import api, fields, models
from datetime import datetime, date, time, timedelta
from dateutil import parser

class isep_pagos(models.Model):
    _name = 'isep.pagos'
    _description = "Pagos ISEP"
    name = fields.Char(string='Nombre', size=128, required=True)
    origin = fields.Char(string="Origen")
    fecha = fields.Datetime(string='Fecha')
    importe = fields.Float(string='Importe', digits=(12, 2))
    lines_ids = fields.One2many('isep.pagoslineas','pago_id',string='lineas')

    @api.model
    def create(self, vals):
        return super(isep_pagos, self).create(vals)


class isep_pagoslineas(models.Model):
    _name = 'isep.pagoslineas'
    _description = "Lineas Pagos ISEP"
    pago_id = fields.Many2one('isep.pagos')
    name = fields.Char(string='Nombre', size=128, required=True)
    fecha = fields.Datetime(string='Fecha')
    importe = fields.Float(string='Importe', digits=(12, 2))
    fecha_informe = fields.Date(string="Fecha informe", compute="_get_fecha_informe")

    @api.multi
    def _get_fecha_informe(self):
        for sel in self:
            d = sel.fecha.strftime('%Y-%m-%d')
            sel.fecha_informe = d