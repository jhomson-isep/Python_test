from odoo import models, fields


class OpFaculty(models.Model):
    _inherit = 'op.faculty'

    job_title = fields.Char(string='Job title', size=128)
    specialty = fields.Char(string='Specialty', size=128)
    workplace_ids = fields.Many2many('op.workplace', string='Workplace')
    nifp = fields.Char(string='NIFP', size=20)
