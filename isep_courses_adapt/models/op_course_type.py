# -*- coding: utf-8 -*-

from odoo import models, fields


class OpCourseType(models.Model):
    _name = "op.course.type"
    _description = "Course type"

    name = fields.Char('Name', size=32, required=True)
    code = fields.Char('Code', size=12, required=True)

    _sql_constraints = [
        ('unique_course_type_code',
         'unique(code)', 'Code should be unique per course type!')]
