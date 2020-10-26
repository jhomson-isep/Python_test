from odoo import models, fields


class HelpDesk(models.Model):
    _inherit = 'helpdesk.ticket'
    ticket_res = fields.Many2many('res.partner',
                                  string="Responsable del ticket")
