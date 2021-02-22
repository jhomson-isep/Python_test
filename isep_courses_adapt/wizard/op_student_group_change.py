# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.isep_courses_adapt.models.moodle import MoodleLib
import logging

logger = logging.getLogger(__name__)


class OpStudentGroupChangeWizard(models.TransientModel):
    _name = 'op.student.group.change.wizard'
    _description = "Change Group of Student"

    op_admission_id = fields.Many2one("op.admission", string="Admission")
    op_modality_id = fields.Many2one("op.modality", string="Modality")
    op_course_id = fields.Many2one("op.course", string="Course")
    op_batch_id = fields.Many2one("op.batch", string="Batch")
    moodle_course_line_ids = fields.One2many(
        'op.moodle.courses.wizard', 'group_change_wizard',
        string='Course lines')

    def get_student_id(self):
        student_id = self.env.context.get('active_ids', []) or []
        records = self.env['op.student'].browse(student_id).id
        return records

    @api.onchange('op_admission_id')
    def set_admission_domain(self):
        return {'domain': {
            'op_admission_id': [('student_id', '=', self.get_student_id())]}}

    @api.onchange('op_course_id', 'op_modality_id')
    def set_batch_domain(self):
        return {'domain': {
            'op_batch_id': [('code', 'ilike', self.op_course_id.code),
                            ('code', 'ilike', self.op_modality_id.code)]}}

    @api.onchange('op_batch_id')
    def get_moodle_courses(self):
        if len(self.moodle_course_line_ids) > 0:
            self.update({'moodle_course_line_ids': [(5, 0, 0)]})
        if self.op_batch_id:
            category = self._get_category()
            print(category.id, category.code)
            logger.info("Category code: {}".format(category.code))
            logger.info("Category id: {}".format(category.id))
            moodle = MoodleLib()
            response = moodle.get_course_by_field(
                field="category", value=category.moodle_category)
            moodle_courses = response['courses']
            moodle_courses.sort(key=self.get_moodle_course_order)
            lines = []
            for i, mdl_course in enumerate(moodle_courses):
                if ('ELR' in self.op_batch_id.code or 'ENR' in self.op_batch_id.code) and i == 0:
                    line = {
                        'moodle_course_id': 2905,
                        'course_name': 'Portal del alumno - ELR',
                        'group_change_wizard': self.id,
                        'selected': True
                    }
                    lines.append((0, 0, line))
                    # self.update({'moodle_course_line_ids': [(0, 0, line)]})
                line = {
                    'moodle_course_id': mdl_course.get('id'),
                    'course_name': mdl_course.get('fullname'),
                    'group_change_wizard': self.id,
                    'selected': i == 0
                }
                lines.append((0, 0, line))

            logger.info(" -------- mdl_course lines --------")
            logger.info(lines)
            self.update({'moodle_course_line_ids': lines})

    @staticmethod
    def get_moodle_course_order(course):
        return course.get('sortorder')

    def modified_data_in_models(self):
        student = self.env['op.student'].search(
            [('id', '=', self.get_student_id())])
        older_category = self._get_older_category()
        older_batch = self.op_admission_id.batch_id
        mdl = MoodleLib()
        mdl_user = mdl.get_user_by_field(field='email',
                                         value=student.partner_id.email.lower())
        if mdl_user is None:
            raise ValidationError(
                _('No se encontro el usuario en moodle'))
        body = '''
        <h1><strong>Se ha realizado cambio de grupo</strong></h1>

        <h2><strong>Datos del grupo anterior</strong></h2>
        '''
        body += (
            '''
        <p><strong>Numero de aplicion:</strong> %s </p>
        <p><strong>Curso:</strong> %s</p>
        <p><strong>Grupo:</strong> %s</p>
        <p><strong>Fecha de admision:</strong> %s</p>
        '''
            % (
                self.op_admission_id[0].application_number,
                self.op_admission_id[0].course_id.name,
                self.op_admission_id[0].batch_id.code,
                self.op_admission_id[0].admission_date,
            )
        )

        op_student_course = self.env['op.student.course'].search(
            [('student_id', '=', self.get_student_id()),
             ('course_id', '=', self.op_admission_id.course_id.id)])
        op_exam_attendees = self.env['op.exam.attendees'].search(
            [('student_id', '=', self.get_student_id()),
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
        body += (
            '''
        <h2><strong>Datos del nuevo grupo</strong></h2>

        <p><strong>Numero de aplicion:</strong> %s </p>
        <p><strong>Curso:</strong> %s</p>
        <p><strong>Grupo:</strong> %s</p>
        <p><strong>Fecha de admision:</strong> %s</p>

        '''
            % (
                op_admission.application_number,
                op_admission.course_id.name,
                op_admission.batch_id.code,
                op_admission.admission_date,
            )
        )
        student.message_post(body=body)

        # ========== Moodle ==========
        enrolled_courses = mdl.get_users_courses(user_id=mdl_user.get('id'))
        print("Enrolled courses: ", enrolled_courses)
        # Delete user from Cohort
        if 'ATH' in older_batch.code or 'PRS' in \
                older_batch.code:
            moodle_cohort = mdl.get_cohort(
                name=older_batch.code)
            mdl.cohort_delete_cohort_members(
                cohort_id=moodle_cohort.get('id'),
                user_id=mdl_user.get('id'))
            # Set new cohort
            new_cohort = mdl.get_cohort(
                name=self.op_batch_id.code)
            if new_cohort is None:
                new_cohort = mdl.core_cohort_create_cohorts(
                    name=self.op_batch_id.code)
            cohort_member = mdl.core_cohort_add_cohorts_members(
                cohortid=new_cohort.get('id'), userid=mdl_user.get('id'))
            logger.info(cohort_member)

        for enrolled_course in enrolled_courses:
            print("------ Area de interes ------")
            print(enrolled_course.get('category'), older_category.moodle_category)
            if enrolled_course.get('category') == older_category.moodle_category:
                # Delete user from group
                print(enrolled_course.get('id'))
                print(older_batch.code)
                mdl_group = mdl.get_group(
                    course_id=enrolled_course.get('id'),
                    group_id=older_batch.code)
                print(mdl_group)
                mdl.delete_group_member(group_id=mdl_group.get('id'),
                                        user_id=mdl_user.get('id'))
                # Unenrol student
                unenrol_request = mdl.unenrol_user(
                    course_id=enrolled_course.get('id'),
                    user_id=mdl_user.get('id'))
                print(unenrol_request)

        # New course enroll
        moodle_course_ids = self.env[
            'op.moodle.courses.wizard'].get_moodle_course_by_group_change(
            self.id)
        if len(moodle_course_ids) > 0:
            moodle_groups = []
            for moodle_course_id in moodle_course_ids:
                moodle_group = mdl.get_group(course_id=moodle_course_id,
                                             group_id=self.op_batch_id.code)
                if moodle_group is None:
                    moodle_group = mdl.core_group_create_groups(
                        self.op_batch_id.code, moodle_course_id)
                logger.info("moodle_group: {}".format(moodle_group))
                moodle_groups.append(moodle_group)
            for moodle_course_id in moodle_course_ids:
                enrol_result = mdl.enrol_user(course_id=moodle_course_id,
                                              user_id=mdl_user.get('id'))
                logger.info(enrol_result)
            # Add new group
            for moodle_group in moodle_groups:
                logger.info(moodle_group)
                if type(moodle_group) == dict:
                    member_result = mdl.add_group_members(
                        group_id=moodle_group.get('id'),
                        user_id=mdl_user.get('id'))
                else:
                    member_result = mdl.add_group_members(
                        group_id=moodle_group[0].get('id'),
                        user_id=mdl_user.get('id'))
                logger.info(member_result)

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
            self.modified_data_in_models()

    @api.depends('op_admission_id')
    def _get_older_category(self):
        code_batch = self.op_admission_id.batch_id.code
        logger.info("course id: {}".format(
            self.op_admission_id.batch_id.course_id.id))
        if "ATH" in code_batch:
            category = self.env['op.moodle.category.rel'].search(
                [('code', '=', 'ATH'),
                 ('course_id', '=',
                  self.op_admission_id.batch_id.course_id.id)], limit=1)
        elif "ELR" in code_batch or "ENR" in code_batch:
            category = self.env['op.moodle.category.rel'].search(
                [('code', '=', 'ELR'),
                 ('course_id', '=',
                  self.op_admission_id.batch_id.course_id.id)], limit=1)
        else:
            logger.info(code_batch)
            code_batch = code_batch[2:10]
            logger.info(code_batch)
            logger.info(self.op_admission_id.batch_id.course_id.id)
            category = self.env['op.moodle.category.rel'].search(
                [('code', '=', code_batch),
                 ('course_id', '=',
                  self.op_admission_id.batch_id.course_id.id)], limit=1)
        print(category.code, category.id)
        logger.info(category)
        logger.info("Category code: {}".format(category.code))
        logger.info("Category id {}".format(category.id))
        return category

    @api.depends('op_batch_id')
    def _get_category(self):
        code_batch = self.op_batch_id.code
        logger.info("course id: {}".format(self.op_batch_id.course_id.id))
        if "ATH" in code_batch:
            category = self.env['op.moodle.category.rel'].search(
                [('code', '=', 'ATH'),
                 ('course_id', '=', self.op_batch_id.course_id.id)], limit=1)
        elif "ELR" in code_batch or "ENR" in code_batch:
            category = self.env['op.moodle.category.rel'].search(
                [('code', '=', 'ELR'),
                 ('course_id', '=', self.op_batch_id.course_id.id)], limit=1)
        else:
            logger.info(code_batch)
            code_batch = code_batch[2:10]
            logger.info(code_batch)
            logger.info(self.op_batch_id.course_id.id)
            category = self.env['op.moodle.category.rel'].search(
                [('code', '=', code_batch),
                 ('course_id', '=', self.op_batch_id.course_id.id)], limit=1)
        print(category.code, category.id)
        logger.info(category)
        logger.info("Category code: {}".format(category.code))
        logger.info("Category id {}".format(category.id))
        return category
