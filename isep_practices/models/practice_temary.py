from odoo import fields, models

class PracticeTemary(models.Model):
    _name = 'practice.temary'
    _description = "Temary"

    content = fields.Char(string='Content', size=300, required=True)
    op_course_id = fields.Many2one('op.course', string="Course", required=True)
    name = fields.Char(string='Name', size=200, required=True)
