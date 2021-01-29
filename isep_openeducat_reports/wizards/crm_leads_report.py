# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

logger = logging.getLogger(__name__)


class CrmLeaReportWizard(models.TransientModel):
    _name = 'crm.lead.report'
    date_init = fields.Date("Initial Date:")
    date_end = fields.Date("End Date:")

    def print_crm_lead_report(self):
        pass