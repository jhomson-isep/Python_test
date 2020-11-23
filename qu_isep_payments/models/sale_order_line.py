# -*- coding: utf-8 -*-
# © 2018 Qubiq 2010
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields
import logging
_logger = logging.getLogger(__name__)


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    grupo_referencia = fields.Char(string="Grupo de referencia")

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(sale_order_line, self).product_id_change()
        if self.product_id.tipodecurso == 'mat':
            self.update({'name': 'Matrícula'})
        return res
