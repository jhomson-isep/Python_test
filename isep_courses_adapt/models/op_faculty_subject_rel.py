from odoo import fields, models, api


class OpFacultySubject(models.Model):
    _name = 'op.faculty.subject.rel'
    _description = 'Faculty Subjects Relations'

    faculty_id = fields.Many2one('op.faculty', string="Faculty")
    subject_id = fields.Many2one('op.subject', string="Subject")




