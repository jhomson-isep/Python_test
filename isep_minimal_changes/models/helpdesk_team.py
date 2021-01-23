# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class HelpDeskTeam(models.Model):
    _inherit = 'helpdesk.team'
    ticket_notify = fields.Many2many('res.partner',
                                     string="Notificar a:")
    alias_email = fields.Char(string='Email del Equipo: ',
                              compute='_helpdesk_team_email')

    @staticmethod
    def get_partner_emails(partner_ids):
        emails = [partner.email for partner in partner_ids if partner.email]
        return ', '.join(emails)

    @api.multi
    def _helpdesk_team_email(self):
        for team in self:
            if team.alias_id and team.alias_id.alias_name and team.alias_id.alias_domain.domain_name:
                team.alias_email = '@'.join([team.alias_id.alias_name,
                                             team.alias_id.alias_domain.domain_name])
