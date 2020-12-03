# -*- coding: utf-8 -*-

from odoo import models, fields

class OpPeriodCourse(models.Model):
    _name = 'op.period.course'
    _description = 'Period of courses'

    name = fields.Char(string="Period Name", size=180)
    code = fields.Char(string="Period Code", size=16)
