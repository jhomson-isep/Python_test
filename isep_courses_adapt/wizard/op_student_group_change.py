# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

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

    @api.onchange('op_course_id')
    def setDomainBatch(self):
        return {'domain': {
            'op_batch_id': [('code', 'ilike', self.op_course_id.code),
                            ('code', 'ilike', self.op_modality_id.code)]}}










