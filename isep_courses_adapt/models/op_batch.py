# -*- coding: utf-8 -*-

from odoo import fields, models, api
import logging

logger = logging.getLogger(__name__)

TOKEN = "3de3ace98f80a5b1e16c84a378d72741"
URL = "https://isep.moodlecloud.com"
ENDPOINT = "/webservice/rest/server.php"


class op_batch(models.Model):
    _inherit = "op.batch"

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
    rvoe_program = fields.Boolean(string='RVOE program', default=False)
    ects = fields.Integer("ECTS", default=0, related='course_id.ects')
    hours = fields.Float(string="Hours", related='course_id.hours')
    expiration_days = fields.Integer("Expiration days", default=0)
    date_diplomas = fields.Datetime("Date diplomas")
    modality_id = fields.Many2one('op.modalidad', string='Modality', related='course_id.modality_id')
    user_company_id = fields.Integer(string="Company id", compute='_get_current_user')
    subject_count = fields.Integer(compute='_compute_subject_count')
    student_count = fields.Integer(compute='_compute_student_count')

    @api.depends()
    def _get_current_user(self):
        for rec in self:
            rec.user_company_id = self.env.user.company_id

    def _compute_subject_count(self):
        """Compute the number of distinct subjects linked to the batch."""
        for batch in self:
            sub_count = len(batch.course_id.subject_ids)
            batch.subject_count = sub_count

    def action_open_subjects(self):
        """Display the linked subjects and adapt the view to the number of records to display."""
        self.ensure_one()
        subjects = self.course_id.subject_ids
        action = self.env.ref('openeducat_core.act_open_op_subject_view').read()[0]
        if len(subjects) > 1:
            action['domain'] = [('id', 'in', subjects.ids)]
        elif len(subjects) == 1:
            form_view = [(self.env.ref('openeducat_core.view_op_subject_form').id, 'form')]
            if 'views' in action:
                logger.info("=== LINE 52 ===")
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                logger.info("=== LINE 55 ===")
                action['views'] = form_view
            action['res_id'] = subjects.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _compute_student_count(self):
        """Compute the number of distinct students linked to the batch."""
        for student in self:
            sub_count = len(student.student_lines)
            student.student_count = sub_count

    def action_open_students(self):
        """Display the linked students and adapt the view to the number of records to display."""
        self.ensure_one()
        students = self.student_lines
        action = self.env.ref('openeducat_core.act_open_op_student_view').read()[0]
        if len(students) > 1:
            action['domain'] = [('batch_id', 'in', students.ids)]
        elif len(students) == 1:
            form_view = [(self.env.ref('openeducat_core.view_op_student_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = students.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
