# -*- coding: utf-8 -*-

from odoo import models, fields
import logging
from .op_moodle import Moodle

logger = logging.getLogger(__name__)

class OpStudentAccess(models.Model):
    _name = "op.student.access"
    _description = "Student Access"

    student_access = fields.Datetime('Student Access', required=True, default=fields.Datetime.now())
    student_id = fields.Many2one('op.student', 'Student', required=True)

    def import_student_access(self):
        mdl = Moodle()
        logger.info("**************************************")
        logger.info("import student access")
        logger.info("**************************************")
        student = self.env['op.student'].search([('id', '=', id)])
        #student = self.env['op.student'].search([('document_number', '=', student.document_number)])
        #rows = mdl.get_last_access('email', student.EMail)
        rows = mdl.get_last_access('email', student.email)
        int_break = 0
        for batch in rows:
            course_code = str(batch.Curso_Id)


