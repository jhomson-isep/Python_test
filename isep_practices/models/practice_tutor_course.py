from odoo import fields, models

class PracticeTutorCourse(models.Model):
    _name = 'practice.tutor.course'
    _description = "Association course with tutor"
    _rec_name = 'op_course_id'

    op_course_id = fields.Many2one('op.course', string="Course", required=True)
    practice_tutor_id = fields.Many2one('practice.tutor', string="Tutor", required=True)
