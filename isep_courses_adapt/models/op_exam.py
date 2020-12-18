# -*- coding: utf-8 -*-
from odoo import models, fields, api


class OpExam(models.Model):
    _inherit = "op.exam"

    exam_code = fields.Char('Exam Code', size=32, required=True)


class OpExamSession(models.Model):
    _inherit = "op.exam.session"


class OpExamAttendees(models.Model):
    _inherit = "op.exam.attendees"

    original_marks = fields.Char(string='Original marks', size=32)
    course_type = fields.Char(string='Type of course', size=32)
    order = fields.Char(string='Order', size=5)
    modify = fields.Char(string='Modify', size=1)
    is_final = fields.Boolean(string='Is Final', default=False)
    admission_id = fields.Many2one('op.admission', compute='_get_admission',
                                   store=True)

    @api.multi
    @api.depends('batch_id', 'student_id', 'course_id')
    def _get_admission(self):
        for sel in self:
            sel.admission_id = sel.env['op.admission'].search(
                [['student_id', '=', sel.student_id.id],
                 ['batch_id', '=', sel.batch_id.id],
                 ['course_id', '=', sel.course_id.id]]).id
