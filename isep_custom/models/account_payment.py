# -*- coding: utf-8 -*-

from openerp import api, models
import logging

_logger = logging.getLogger(__name__)


class account_payment(models.Model):
    _inherit = 'account.payment'

    """
    Se realiza la herencia para quitar el amount por defecto y asi no vayan
    validando pagos con todo el importe...
    """
    @api.model
    def default_get(self, fields):
        rec = super(account_payment, self).default_get(fields)
        if 'amount' in rec:
            rec['amount'] = 0.0
        return rec

