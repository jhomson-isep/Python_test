# -*- coding: utf-8 -*-
from odoo import models, fields

<<<<<<< HEAD
class OpMoodleCategoryRel(models.Model):
    _name = 'op.moodle.category.rel'
    _description = "Moodle Relation Course"
    
=======

class OpMoodleCategoryRel(models.Model):
    _name = 'op.moodle.category.rel'
    _description = "Moodle Relation Course"

>>>>>>> origin/feature/321-cohorts-moodle
    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    moodle_category = fields.Integer(string="Moodle category", required=True)
    moodle_module = fields.Integer()
    modality_id = fields.Many2many('op.modality', required=True)
    course_id = fields.Many2one('op.course', required=True)
