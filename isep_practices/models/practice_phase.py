from odoo import fields, models

class PracticePhase(models.Model):
    _name = 'practice.phase'

    code = fields.Char(string='Code', size=8)
    name = fields.Char(string='Name', size=200)

    _sql_constraints = [(
        'unique_code',
        'unique(code)',
        'Code must be unique per phase!'
    )]