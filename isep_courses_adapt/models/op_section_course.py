# -*- coding: utf-8 -*-

from odoo import models, fields

class OpSectionCourse(models.Model):
    _name = "op.section.course"
    _description = "Section of courses"

    name = fields.Char(string="Section name", size=200, required=True)
    code = fields.Char('Section Code', size=16, required=True)
