# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime

class OpStudentExtendDueDate(models.TransientModel):
    _name = "op.student.extend.due.date.wizard"
    _description = "Modify due date in admission of student"

    @api.model
    def _get_domain(self):
        student_id = self.env.context.get('active_ids', []) or []
        student = self.env['op.student'].browse(student_id).id
        return [('student_id.id', '=', str(student))]

    admission_ids = fields.Many2many(
        'op.admission',
        string='Admissions',
        required=True,
        help="Select one or more admissions",
        domain=_get_domain
    )
    months_to_extend = fields.Integer(
        string='Months',
        required=True,
        help="Number of months to extend",
        default=1
    )

    def extend(self):
        for admission in self.admission_ids:
            new_date = self.calculate_date(admission.due_date)
            print(new_date)

    def calculate_date(self, due_date):
        due_date = datetime.datetime(due_date.year, due_date.month, due_date.day)
        due_seconds = datetime.datetime.timestamp(due_date)
        months_seconds = self.months_to_extend * 2.628e+6
        new_date = due_seconds + months_seconds
        return datetime.datetime.fromtimestamp(new_date).date()
