from odoo import models, fields


class HelpDesk(models.Model):
    _inherit = 'helpdesk.ticket'
    ticket_res = fields.Many2many('res.partner',
                                  string="Responsable del ticket")


class HelpdeskStage(models.Model):
    _inherit = 'helpdesk.stage'

    active = fields.Boolean(string='active', default=True)


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.stage'

    personal_team_email = fields.Char(string='Email personal')
