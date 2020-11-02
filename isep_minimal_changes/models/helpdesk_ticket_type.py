from odoo import models, fields


class HelpdeskTicketType(models.Model):
    _inherit = 'helpdesk.ticket.type'

    active = fields.Boolean(string='active', default=True)
