# -*- coding: utf-8 -*-

from odoo import models, fields
import logging
from .op_moodle import Moodle
import datetime

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
        student = self.env['op.student'].search([('id', '=', self.student_id.id)])
        rows = mdl.get_last_access('email', student.document_number)
        int_break = 0
        for row in rows:
            ult_access=datetime.datetime.utcfromtimestamp(row['lastaccess'])
            self.write({'student_id': self.student_id,
                        'student_access':ult_access})


