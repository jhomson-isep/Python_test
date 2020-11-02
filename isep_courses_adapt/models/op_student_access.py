# -*- coding: utf-8 -*-

from odoo import models, fields
import logging
#from .op_moodle import Moodle

logger = logging.getLogger(__name__)

class OpStudentAccess(models.Model):
    _name = "op.student.access"
    _description = "Student Access"

    student_access = fields.Datetime('Student Access', required=True, default=fields.Datetime.now())
    student_id = fields.Many2one('op.student', 'Student', required=True)


