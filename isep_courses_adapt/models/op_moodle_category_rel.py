# -*- coding: utf-8 -*-
from odoo import models, fields

class op_moodle_category_rel(models.Model):
    _name = 'op.moodle.category.rel'
    _description = "Moodle Relation Course"
    
    name = fields.Char()
    moodle_category = fields.Integer()
    moodle_module = fields.Integer()
    modality_id = fields.Many2many('op.modality')
    course_id = fields.Many2one('op.course')
