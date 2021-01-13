from odoo import models, fields


class HelpDesk(models.Model):
    _inherit = 'helpdesk.ticket'

    reminder_date = fields.Date(string="Fecha del recordatorio")
    reminder_name = fields.Char(string="Nombre del recordatorio")
