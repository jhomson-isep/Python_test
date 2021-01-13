from odoo import fields, models

class PracticeTemary(models.Model):
    _name = 'practice.temary'

    content = fields.Char(string='Content', size=300)
    op_course_id = fields.Many2one('op.course', string="Course")
    name = fields.Char(string='Name', size=200)
