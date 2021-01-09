# -*- coding: utf-8 -*-
from odoo import models, fields, api

class OpStudentMergeWizard(models.TransientModel):
    _name = 'op.student.merge.wizard'
    _description = "Merge Student for selected Student(s)"

    def _get_students(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []

    student_ids = fields.Many2many(
        'op.student', default=_get_students, string='Students')


    def action_merge(self):
        print("Merge Students!!!")