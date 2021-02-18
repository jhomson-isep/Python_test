# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.isep_courses_adapt.models.moodle import MoodleLib

class OpStudentGroupChangeWizard(models.TransientModel):
    _name = 'op.student.group.change.wizard'
    _description = "Change Group of Student"

    op_admission_id = fields.Many2one("op.admission", string="Admission")
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
        student = self.env['op.student'].search([('id', '=', self.getIdStudent())])
        mdl = MoodleLib()
        mdl_course = mdl.get_course(self.op_admission_id.batch_id.moodle_code)
        if mdl_course is None:
            raise ValidationError(
                _('No se encontro el curso en Moodle'))
        mdl_group = mdl.get_group(mdl_course.get('id'),
                                    self.op_admission_id.batch_id.code)
        if mdl_group is None:
            raise ValidationError(
                _('No se encontro el grupo en moodle!!'))
        mdl_user = mdl.get_user(field='email',
                                value=student.partner_id.email.lower())
        if mdl_user is None:
            raise ValidationError(
                _('No se encontro el usuario en moodle'))
        body = '''
        <h1><strong>Se ha realizado cambio de grupo</strong></h1>

        <h2><strong>Datos del grupo anterior</strong></h2>
        '''
        body = body + '''
        <p><strong>Numero de aplicion:</strong> %s </p>
        <p><strong>Curso:</strong> %s</p>
        <p><strong>Grupo:</strong> %s</p>
        <p><strong>Fecha de admision:</strong> %s</p>
        '''%(self.op_admission_id[0].application_number,
            self.op_admission_id[0].course_id.name,
            self.op_admission_id[0].batch_id.code,
            self.op_admission_id[0].admission_date)
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
        body = body + '''
        <h2><strong>Datos del nuevo grupo</strong></h2>

        <p><strong>Numero de aplicion:</strong> %s </p>
        <p><strong>Curso:</strong> %s</p>
        <p><strong>Grupo:</strong> %s</p>
        <p><strong>Fecha de admision:</strong> %s</p>

        '''%(op_admission.application_number,
            op_admission.course_id.name,
            op_admission.batch_id.code,
            op_admission.admission_date)
        student.message_post(body=body)
        mdl_new_group = mdl.get_course(op_admission.batch_id.moodle_code)
        mdl.delete_group_member(mdl_group.get('id'),
                                mdl_user.get('id'))
        mdl.add_group_members(mdl_new_group.get('id'),
                              mdl_user.get('id'))
    
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
