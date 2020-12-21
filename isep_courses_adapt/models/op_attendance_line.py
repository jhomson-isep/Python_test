# -*- coding: utf-8 -*-
from odoo import models, fields
import logging

logger = logging.getLogger(__name__)

class OpAttendanceLine(models.Model):
    _inherit = 'op.attendance.line'

    justified = fields.Boolean(string="Justified", default=False)

    def set_register_id(self):
        attendances = self.search([])
        for attendance in attendances:
            attendance.write({
                'register_id' : attendance.attendance_id.register_id.id
            })
            logger.info("**************************************")
            logger.info("set name %s" % attendance.id)
            logger.info("**************************************")