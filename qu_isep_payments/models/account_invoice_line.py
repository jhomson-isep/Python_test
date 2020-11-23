# -*- coding: utf-8 -*-
# © 2018 Qubiq 2010
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import api, fields, models
_logger = logging.getLogger(__name__)


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'
    price_unit_report = fields.Float(string="Precio unidad con Financiación prorrateada", compute="_get_price_unit_report")
    price_subtotal_report = fields.Float(string="Precio subtotal con Financiación prorrateada", compute="_get_price_subtotal_report")

    """
    Dado que en el informa no se requiere la linea de financiacion se tiene
    que distribuir ese precio en todas las lineas de cursos.
    """
    @api.multi
    def _get_price_unit_report(self):
        for sel in self:
            sel.price_unit_report = '%.2f'%((sel.price_subtotal_report / (1-(sel.discount/100.0))) / sel.quantity)

    """
    Funcion que calcula el precio total de un producto con las prorratas
    de la factura y el precio subtotal.
    """
    @api.multi
    def _get_price_subtotal_report(self):
        for sel in self:
            sel.price_subtotal_report = sel.price_subtotal + sel.invoice_id.prorata_financiacion_lineas
