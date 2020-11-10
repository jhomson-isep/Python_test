# -*- coding: utf-8 -*-
from odoo import models, fields
import logging

logger = logging.getLogger(__name__)


class HelpDeskTeam(models.Model):
    _inherit = 'helpdesk.team'
    ticket_notify = fields.Many2many('res.partner',
                                     string="Notificar a:")

    @staticmethod
    def get_partner_emails(partner_ids):
        emails = []
        for partner in partner_ids:
            if partner.email:
                emails.append(partner.email)
        return ', '.join(emails)
