# -*- coding: utf-8 -*-
# © 2018 Qubiq 2010
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
import dateutil.parser
from . import numeros

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
    ImporteTexto = fields.Char(string="Importe en Texto")

    @api.multi
    def _get_fecha_informe(self):
        for sel in self:
            sel.fecha_informe = dateutil.parser.parse(sel.fecha).date()
            


    @api.multi 
    def on_cambio(self, cr, uid, ids, importe, context=None):
        self.ImporteTexto = numero_a_letras(self.importe)
    
    @api.multi
    def write(self, vals):
        vals['ImporteTexto'] = numero_a_letras(self.importe)
        return super(isep_pagoslineas, self).write(vals)
