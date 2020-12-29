# -*- coding: utf-8 -*-
from odoo import models, fields
import logging

logger = logging.getLogger(__name__)

class OpAttendanceLine(models.Model):
    _inherit = 'op.attendance.line'

    justified = fields.Boolean(string="Justified", default=False)

    def set_register_id(self):
        logger.info("**************************************")
        logger.info("set register id in all atendances line")
        logger.info("**************************************")
        attendances = self.search([])
        for attendance in attendances:
            attendance.write({
                'register_id': attendance.attendance_id.register_id.id
            })
            logger.info("**************************************")
            logger.info("update line id %s" % attendance.id)
            logger.info("**************************************")
        logger.info("**************************************")
        logger.info("End of script")
        logger.info("**************************************")

    def import_all_attendances_moodle(self):
        self.env['op.attendance.sheet'].set_name_attendance_sheet()
