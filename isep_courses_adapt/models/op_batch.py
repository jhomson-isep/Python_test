# -*- coding: utf-8 -*-

from odoo import fields, models, api
from .op_sql import SQL
import logging

logger = logging.getLogger(__name__)

TOKEN = "3de3ace98f80a5b1e16c84a378d72741"
URL = "https://isep.moodlecloud.com"
ENDPOINT = "/webservice/rest/server.php"


class OpBatch(models.Model):
    _inherit = "op.batch"

    start_date = fields.Date('Start Date', default=fields.Date.today())
    end_date = fields.Date('End Date')
    student_lines = fields.One2many('op.student.course', 'id')
    moodle_course_id = fields.Integer(string="Moodle Id")
    academic_year = fields.Char(string="Academic Year", size=16)
    days_week = fields.Char(string="Days week", size=50)
    schedule = fields.Char(string="Schedule", size=200)
    preference_group = fields.Char(string="Preference group", size=200)
    class_place = fields.Char(string="Class place", size=200)
    type_practices = fields.Many2one('op.practices.type', string='Type practices')
    campus_id = fields.Many2one('op.campus', string='Campus')
    coordinator = fields.Many2one('res.partner', string="Coordinator")
    uvic_program = fields.Boolean(string='UVIC program', default=False)
    rvoe_program = fields.Boolean(string='RVOE program', default=False)
    ects = fields.Integer(string="ECTS", default=0, related='course_id.ects')
    hours = fields.Float(string="Hours", related='course_id.hours')
    expiration_days = fields.Integer(string="Expiration days", default=0)
    date_diplomas = fields.Datetime(string="Date diplomas")
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

    def import_batches(self):
        s = SQL()
        logger.info("**************************************")
        logger.info("import batches")
        logger.info("**************************************")
        rows = s.get_all_courses()
        int_break = 0
        for batch in rows:
            existent_batch = self.search([('code', '=', batch.Curso_Id)])
            if len(existent_batch) < 1:
                try:
                    course = self.env['op.course'].search([('code', 'ilike', batch.code)], limit=1)
                    partner = self.env['res.partner'].search([('name', 'ilike', batch.Coordinador)], limit=1)
                    if batch.Coordinador is not None:
                        if len(partner) != 0:
                            partner = self.env['res.partner'].create({'name': batch.Coordinador})
                    campus = self.env['op.campus'].search([('name', 'ilike', batch.Marca)], limit=1)
                    if batch.Marca is not None:
                        if len(campus) != 0:
                            campus = self.env['op.campus'].create({'name': batch.Marca})
                    practices = self.env['op.practices.type'].search([('name', 'ilike', batch.TipoPracticas)], limit=1)
                    logger.info("practices: ".format(batch.TipoPracticas))
                    if batch.TipoPracticas is not None and batch.TipoPracticas != 0:
                        if len(practices) != 0:
                            practices = self.env['op.practices.type'].create({'name': batch.TipoPracticas})

                    batch_values = {
                        'name': batch.Curso_Id,
                        'code': batch.Curso_Id,
                        'course_id': course.id,
                        'start_date': batch.FechaInicio or batch.FechaAlta,
                        'end_date': batch.FechaFin or fields.Date.today(),
                        'coordinator': partner.id or None,
                        'campus_id': campus.id or None,
                        'date_diplomas': batch.FechaDiplomas,
                        'academic_year': batch.AnyAcademico,
                        'days_week': batch.DiaSemana,
                        'schedule': batch.Horario,
                        'class_place': batch.LugarClase,
                        'type_practices': practices.id or None
                    }

                    if course.id:
                        res = super(OpBatch, self).create(batch_values)
                        print(res)

                    # if int_break == 5:
                    #     break
                    # int_break += 1
                except Exception as e:
                    logger.info(e)
                    continue
