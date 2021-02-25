# -*- coding: utf-8 -*-
from odoo import models, fields, api
from .op_mysql import MYSQL
import traceback
import logging

logger = logging.getLogger(__name__)


class OpExam(models.Model):
    _inherit = "op.exam"

    exam_code = fields.Char('Exam Code', size=32, required=True)

    def generate_exams_from_batch_code(self, code):
        batch = self.env['op.batch'].search([('code', '=', code)])
        batch_subjects = self.env['op.batch.subject.rel'].search([(
            'batch_id', '=', batch.id)])
        exams_count = self.search_count([('batch_id', '=', batch.id)])
        if len(batch_subjects) > exams_count:
            for batch_subject in batch_subjects:
                try:
                    exam_session = self.env['op.exam.session'].search([(
                        'batch_id', '=', batch.id)], limit=1)
                    exam = self.search([('exam_code', '=', batch.code +
                                         batch_subject.subject_id.code)],
                                       limit=1)
                    if len(exam_session) > 0 and len(exam) == 0:
                        exam_code = batch.code + batch_subject.subject_id.code
                        exam = self.create({
                            'session_id': exam_session.id,
                            'course_id': batch.course_id.id,
                            'batch_id': batch.id,
                            'subject_id': batch_subject.subject_id.id,
                            'exam_code': exam_code,
                            'name': "-".join([batch.code,
                                              batch_subject.subject_id.code]),
                            'start_time': batch.start_date,
                            'end_time': batch.end_date,
                            'total_marks': 10,
                            'min_marks': 7,
                            'state': 'done',
                            'active': True
                        })
                        logger.info("Exam created: {}".format(exam.exam_code))
                    else:
                        if len(exam) > 0:
                            logger.info("Exam Already exist: {}".format(
                                exam.exam_code))
                        if len(exam_session) == 0:
                            logger.info("Exam session not found")
                except Exception as e:
                    logger.info(e)
                    traceback.print_tb(e.__traceback__)
                    continue


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
    marks = fields.Float(string='Marks')
    subject_id = fields.Many2one('op.subject', string='Subject',
                                 related='exam_id.subject_id')

    @api.multi
    @api.depends('batch_id', 'student_id', 'course_id')
    def _get_admission(self):
        for sel in self:
            sel.admission_id = self.env['op.admission'].search(
                [['student_id', '=', sel.student_id.id],
                 ['batch_id', '=', sel.batch_id.id],
                 ['course_id', '=', sel.course_id.id]]).id

    def import_grades_from_moodle(self):
        logger.info('***************************************')
        logger.info('*   [INIT] IMPORT GRADES FROM MOODLE  *')
        logger.info('***************************************')
        mysql = MYSQL()
        grades = mysql.get_moodle_grades()
        for grade in grades:
            try:
                if grade.get('mdl_groups_name') is None or grade.get(
                        'item_idnumber') is None:
                    continue
                session_code = grade.get('mdl_groups_name') + grade.get(
                    'item_idnumber')
                logger.info("Session code:  {}".format(session_code))
                exam = self.env['op.exam'].search(
                    [('exam_code', '=', session_code)], limit=1)
                if len(exam) == 0:
                    self.env['op.exam'].generate_exams_from_batch_code(
                        grade.get('mdl_groups_name'))
                exam = self.env['op.exam'].search(
                    [('exam_code', '=', session_code)], limit=1)
                logger.info("User id: {}".format(grade.get('userid')))
                student = self.env['op.student'].search(
                    [('moodle_id', '=', grade.get('userid'))], limit=1)
                if len(student) > 0 and len(exam) > 0:
                    attendee = self.search(
                        [('student_id', '=', student.id),
                         ('exam_id', '=', exam.id)], limit=1)
                    if len(attendee) == 0:
                        attendee = self.create({
                            'exam_id': exam.id,
                            'student_id': student.id,
                            'batch_id': exam.batch_id.id,
                            'course_id': exam.course_id.id,
                            'marks': grade.get('finalgrade'),
                            'note': grade.get('item_idnumber'),
                            'status': 'present',
                            'is_final': True,
                        })
                        logger.info("Exam attendee created: {}".format(
                            attendee.id))
                    else:
                        if attendee.marks != grade.get('finalgrade'):
                            attendee.update({'marks': grade.get('finalgrade')})
                        logger.info("Attendee already exist: {}, "
                                    "Updating".format(grade))
                else:
                    not_found = "Exam" if exam == 0 else "Student"
                    logger.info(
                        "{} not found: {}".format(not_found, session_code))

            except Exception as e:
                logger.info(e)
                traceback.print_tb(e.__traceback__)
                logger.error(e, exc_info=True)
                continue
        logger.info('***************************************')
        logger.info('*   [END] IMPORT GRADES FROM MOODLE   *')
        logger.info('***************************************')
