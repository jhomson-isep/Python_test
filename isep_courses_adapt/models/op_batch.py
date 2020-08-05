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
    subject_count = fields.Integer(compute='_compute_subject_count')

    def _compute_subject_count(self):
        """Compute the number of distinct subjects linked to the batch."""
        for batch in self:
            sub_count = len(batch.course_id.subject_ids)
            batch.subject_count = sub_count

    def action_open_subjects(self):
        """Display the linked subscription and adapt the view to the number of records to display."""
        self.ensure_one()
        subjects = self.course_id.subject_ids
        action = self.env.ref('openeducat_core.act_open_op_subject_view').read()[0]
        if len(subjects) > 1:
            action['domain'] = [('id', 'in', subjects.ids)]
        elif len(subjects) == 1:
            form_view = [(self.env.ref('openeducat_core.act_open_op_subject_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = subjects.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
