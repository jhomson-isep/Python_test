# -*- coding: utf-8 -*-

from odoo import models, fields
import logging
from .op_moodle import Moodle
import datetime

logger = logging.getLogger(__name__)


class OpStudentAccess(models.Model):
    _name = "op.student.access"
    _description = "Student Access"

    student_access = fields.Datetime('Student Access', required=True,
                                     default=fields.Datetime.now())
    student_id = fields.Many2one('op.student', 'Student', required=True)
    last_access = fields.Char(String='Ago', readonly=True,
                              compute='_get_last_access')

    def _get_last_access(self):
        for record in self:
            access_ago = fields.Datetime.now() - record.student_access
            minutes, seconds = divmod(access_ago.seconds, 60)
            hours, minutes = divmod(minutes, 60)
            access_string = ""
            if access_ago.days > 0:
                if access_ago.days > 365:
                    years, days = divmod(access_ago.days, 365)
                    access_string += "{0} años, {1} días, ".format(years, days)
                else:
                    access_string += "{0} días, ".format(access_ago.days)
            if hours > 0:
                access_string += "{0} horas, ".format(hours)
            if minutes > 0:
                access_string += "{0} minutos, ".format(minutes)
            record.last_access = access_string[:-2]





