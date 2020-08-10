# -*- coding: utf-8 -*-

from odoo import models, fields
from .op_sql import SQL
import logging
import os

logger = logging.getLogger(__name__)


class OpSubject(models.Model):
    _inherit = 'op.subject'

    moodle_course_id = fields.Integer(string='Moodle course Id')
    uvic_code = fields.Char(string="UVIC code", size=16)

    def import_subjects(self):
        s = SQL()
        logger.info("**************************************")
        logger.info("import subjects")
        logger.info("**************************************")
        rows = s.get_all_subjects()
        int_break = 0
        for subject in rows:
            existent_subject = self.search([('code', '=', subject.CodAsignatura)])
            if len(existent_subject) < 1:
                try:
                    subject_values = {
                        'name': subject.NomAsignatura,
                        'code': subject.CodAsignatura,
                        'type': 'theory',
                        'subject_type': 'compulsory',
                        'uvic_code': subject.CodUvic,
                        'moodle_course_id': subject.Moodle
                    }

                    res = super(OpSubject, self).create(subject_values)
                    print(res)

                    if int_break == 50 and os.name != "posix":
                        break
                    int_break += 1
                except Exception as e:
                    logger.info(e)
                    continue
