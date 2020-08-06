# -*- coding: utf-8 -*-

import logging
from openerp import api, fields, models, _
from openerp.exceptions import UserError
import datetime
_logger = logging.getLogger(__name__)


class temp_tax(models.Model):
    _name = 'temp.tax'

    name = fields.Char(string='Nombre de la tasa')
    amount = fields.Float(string="Precio con tasa")
    id_factura = fields.Many2one('account.invoice', string="Id factura")
    base = fields.Float(string='Base sin tasa')
