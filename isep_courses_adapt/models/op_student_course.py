# -*- coding: utf-8 -*-
import traceback

from odoo import models, fields
import logging

logger = logging.getLogger(__name__)


class OpStudentCourse(models.Model):
    _inherit = "op.student.course"

    finish_date = fields.Date(string='Finish Date')

    def set_student_course_subject_rel(self):
        logger.info("**************************************")
        logger.info("import student-course subjects")
        logger.info("**************************************")
        student_courses = self.search([])
        for student_course in student_courses:
            try:
                if len(student_course.batch_id.op_batch_subject_rel_ids) > 0:
                    subjects = self.get_subject_ids_from_rel(
                        student_course.batch_id.op_batch_subject_rel_ids)
                    if len(subjects) > 0:
                        student_course.update(
                            {'subject_ids': [(6, 0, subjects)]})
            except Exception as e:
                logger.info(e)
                traceback.print_exc()
                continue
        logger.info("**************************************")
        logger.info("end of import student-course subjects")
        logger.info("**************************************")

    @staticmethod
    def get_subject_ids_from_rel(subject_rel_ids):
        return [
            subject_rel.subject_id.id
            for subject_rel in subject_rel_ids
            if subject_rel.subject_id.id
        ]
