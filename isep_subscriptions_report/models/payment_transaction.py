# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'payment.transaction'


    #Query para sacar todos las suscripciones con el año actual
    query ="""
    SELECT partner_name, partner_email, reference, amount, date, state FROM payment_transaction WHERE date_part('year',date) = date_part('year',now())
    """

