# -*- coding: utf-8 -*-
from odoo import models, fields
import logging

logger = logging.getLogger(__name__)


class OpAttendanceSheet(models.Model):
    _inherit = 'op.attendance.sheet'

    def set_name_attendance_sheet(self):
        logger.info("**************************************")
        logger.info("set name in all atendances sheets")
        logger.info("**************************************")
        attendances_sheets = self.search([])
        for attendance_sheet in attendances_sheets:
            sheet = self.env['ir.sequence'].next_by_code('op.attendance.sheet')
            register = self.env['op.attendance.register']. \
                browse(attendance_sheet.register_id.id).code
            attendance_sheet.write({
                'name' : register + sheet
            })
            logger.info("**************************************")
            logger.info("set name %s" % (register + sheet))
            logger.info("**************************************")
        logger.info("*****************************************")
        logger.info("End of script: set name in all atendances sheets")
        logger.info("*****************************************")