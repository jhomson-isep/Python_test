# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'sale.subscription'



    def obtain_subscription(self):
        total_subscription = self.env['sale.subscrition'].sudo().search('date', 'like', '2020')

        for subscription in total_subscription:
            logger.info(subscription)
