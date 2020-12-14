# -*- coding: utf-8 -*-
from odoo import models, fields


class OpAttendanceLine(models.Model):
    _inherit = 'op.attendance.line'

    justified = fields.Boolean(string="Justified", default=False)
