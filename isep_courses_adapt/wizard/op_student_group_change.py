# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class OpStudentGroupChangeWizard(models.TransientModel):
    _name = 'op.student.group.change.wizard'
    _description = "Change Group of Student"

    op_admission_id = fields.Many2one("op.admission", string="Admissions")
    op_modality_id = fields.Many2one("op.modality", string="Modality")
    op_course_id = fields.Many2one("op.course", string="Course")
    op_batch_id = fields.Many2one("op.batch", string="Batch")

    def getIdStudent(self):
        student_id = self.env.context.get('active_ids', []) or []
        records = self.env['op.student'].browse(student_id).id
        return records

    @api.onchange('op_admission_id')
    def setDomainAdmission(self):
        return {'domain': {'op_admission_id': [('student_id', '=', self.getIdStudent())]}}

    @api.onchange('op_course_id', 'op_modality_id')
    def setDomainBatch(self):
        return {'domain': {
            'op_batch_id': [('code', 'ilike', self.op_course_id.code),
                            ('code', 'ilike', self.op_modality_id.code)]}}

    def modifiedDataInModels(self):
        op_student_course = self.env['op.student.course'].search(
            [('student_id', '=', self.getIdStudent()),
             ('course_id', '=', self.op_admission_id.course_id.id)])
        op_exam_attendees = self.env['op.exam.attendees'].search(
            [('student_id', '=', self.getIdStudent()),
             ('course_id', '=', self.op_admission_id.course_id.id)])
        op_admission = self.env['op.admission'].search(
            [('id', '=', self.op_admission_id.id)])
        print(op_student_course)
        print(op_exam_attendees)

        if len(op_student_course) > 0:
            values = {
                'batch_id': self.op_batch_id.id,
                'course_id': self.op_course_id.id
            }
            op_student_course.write(values)

        if len(op_exam_attendees) > 0:
            for op_exam_attendee in op_exam_attendees:
                values = {
                    'batch_id': self.op_batch_id.id,
                    'course_id': self.op_course_id.id
                }
                op_exam_attendee.write(values)

        if len(op_admission) > 0:
            values = {
                'batch_id': self.op_batch_id.id,
                'course_id': self.op_course_id.id
            }
            op_admission.write(values)

    def change(self):
        if not self.op_admission_id.id:
            raise ValidationError(
                _("You must select admission."))
        if not self.op_modality_id.id:
            raise ValidationError(
                _("You must select modality."))
        if not self.op_course_id.id:
            raise ValidationError(
                _("You must select course."))
        if not self.op_batch_id.id:
            raise ValidationError(
                _("You must select group."))
        else:
            self.modifiedDataInModels()
