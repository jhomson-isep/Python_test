from odoo import models, fields


class HelpdeskTag(models.Model):
    _inherit = 'helpdesk.tag'

    active = fields.Boolean(string='active', default=True)
