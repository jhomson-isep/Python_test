from odoo import models, fields


class OpFaculty(models.Model):
    _inherit = 'op.faculty'

    title = fields.Char(string='Title', size=128)
    specialty = fields.Char(string='Specialty', size=128)
    workplace = fields.Char(string='Workplace', size=128)
