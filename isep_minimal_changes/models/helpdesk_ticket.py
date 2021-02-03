from odoo import models, fields

MONTHS = [
    ('01', 'Enero'),
    ('02', 'Febrero'),
    ('03', 'Marzo'),
    ('04', 'Abril'),
    ('05', 'Mayo'),
    ('06', 'Junio'),
    ('07', 'Julio'),
    ('08', 'Agosto'),
    ('09', 'Septiembre'),
    ('10', 'Octubre'),
    ('11', 'Noviembre'),
    ('12', 'Diciembre'),
]


class HelpDesk(models.Model):
    _inherit = 'helpdesk.ticket'
    ticket_res = fields.Many2many('res.partner',
                                  string="Responsable del ticket")
    month = fields.Selection(MONTHS, string="Month")
    total_requirements = fields.Integer(string="Total requirements", default=0)
    resolved_requirements = fields.Integer(string="Resolved requirements",
                                           default=0)
    require_project = fields.Boolean(string="Requires project?",
                                     default=False)


class HelpdeskStage(models.Model):
    _inherit = 'helpdesk.stage'

    active = fields.Boolean(string='active', default=True)


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.stage'

    personal_team_email = fields.Char(string='Email personal')
