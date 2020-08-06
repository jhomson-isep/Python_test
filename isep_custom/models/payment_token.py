# -*- coding: utf-8 -*-

from openerp import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class payment_token(models.Model):
    _inherit = 'payment.token'

#    name = fields.Char(required=True)
    csv = fields.Char(string='CSV', size=4)
#   acquirer_ref = fields.Char(size=16)
    caducidad = fields.Date(string='Fecha de caducidad', required=False)

