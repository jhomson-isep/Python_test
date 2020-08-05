# -*- coding: utf-8 -*-

from odoo import fields, models, api
import logging

logger = logging.getLogger(__name__)

TOKEN = "3de3ace98f80a5b1e16c84a378d72741"
URL = "https://isep.moodlecloud.com"
ENDPOINT = "/webservice/rest/server.php"


class op_batch(models.Model):
    _inherit = "op.batch"

    op_batch_subject_rel_ids = fields.One2many('op.batch.subject.rel', 'id')
    student_lines = fields.One2many('op.student.course', 'id')
    moodle_course_id = fields.Integer(string="Moodle Id")
    academic_year = fields.Integer("Academic Year")
    days_week = fields.Char("Days week", size=50)
    schedule = fields.Char("Schedule", size=200)
    preference_group = fields.Char("Preference group", size=200)
    class_place = fields.Char("Class place", size=200)
    type_practices = fields.Many2one('op.practices.type', string='Type practices')
    campus_id = fields.Many2one('op.campus', string='Campus')
    coordinator = fields.Many2one('res.partner', string="Coordinator")
    uvic_program = fields.Boolean(string='UVIC program', default=False)
    ects = fields.Integer("ECTS", default=0, related='course_id.ects')
    hours = fields.Float(string="Hours", related='course_id.hours')
    expiration_days = fields.Integer("Expiration days", default=0)
    date_diplomas = fields.Datetime("Date diplomas")
    modality_id = fields.Many2one('op.modalidad', string='Modality', related='course_id.modality_id')
