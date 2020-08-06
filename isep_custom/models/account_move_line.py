# -*- coding: utf-8 -*-

#from openerp import fields, models, api
import logging
_logger = logging.getLogger(__name__)

import time
from openerp import api, fields, models, _
from openerp.osv import expression
from openerp.exceptions import RedirectWarning, UserError
from openerp.tools.misc import formatLang
from openerp.tools import float_compare, float_is_zero
from openerp.tools.safe_eval import safe_eval

from collections import OrderedDict



class account_move_line(models.Model):
    _inherit = 'account.move.line'
    # Se ha cambiado el order para que el segundo campo de ordenacion
    # sea la fecha de vencimiento para que las conciliaciones de pagos
    # se realizen para los pagos mas antiguos primero.
    _order = "date desc, date_maturity, id desc"

    date_maturity = fields.Date(required=False)
    payment_mode_id = fields.Many2one(readonly=False)

    """
    Se ha sobreescrito para retornar la fecha de vencimiento al final
    """
    @api.multi
    def name_get(self):
        super(account_move_line, self).name_get()
        result = []
        for line in self:
            if line.ref:
                if line.date_maturity:
                    result.append((line.id, (line.move_id.name or '') + '(' + line.ref + ') - ' + str(line.date_maturity)))
                else:
                    result.append((line.id, (line.move_id.name or '') + '(' + line.ref + ')'))
            elif line.date_maturity:
                result.append((line.id, line.move_id.name + ' - ' + str(line.date_maturity)))
            else:
                result.append((line.id, line.move_id.name))
        return result
