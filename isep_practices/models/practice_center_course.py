# -*- encoding: utf-8 -*-
from odoo import fields, models

class PracticeCenterCourse(models.Model):
    _name = 'practice.center.course'
    _description = "Association course with center"
    _rec_name = 'op_course_id'

    op_course_id = fields.Many2one('op.course', string="Course", required=True)
    partner_id = fields.Many2one('res.partner')