# -*- coding: utf-8 -*-

from datetime import date, datetime
from odoo import fields, models, api
from .op_sql import SQL
import logging
import os

logger = logging.getLogger(__name__)

TOKEN = "3de3ace98f80a5b1e16c84a378d72741"
URL = "https://isep.moodlecloud.com"
ENDPOINT = "/webservice/rest/server.php"


class OpBatch(models.Model):
    _inherit = "op.batch"

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    student_lines = fields.One2many('op.student.course', 'id')
    moodle_course_id = fields.Integer(string="Moodle Id")
    credits = fields.Float(string="Credits", related='course_id.credits')
    academic_year = fields.Char(string="Academic Year", size=16)
    days_week = fields.Char(string="Days week", size=50)
    schedule = fields.Char(string="Schedule", size=200)
    preference_group = fields.Char(string="Preference group", size=200)
    generation = fields.Char(string="Generation", size=100)  #Field of generation add
    contact_class = fields.Char(string="Contact", size=200)
    type_practices = fields.Many2one('op.practices.type', string='Type '
                                                                 'practices')
    campus_id = fields.Many2one('op.campus', string='Campus')
    coordinator = fields.Many2one('res.partner', string="Coordinator")
    uvic_program = fields.Boolean(string='UVIC program', default=False)
    sepyc_program = fields.Boolean(string='SEPYC program', default=False)
    ects = fields.Integer(string="ECTS", default=0, related='course_id.ects')
    hours = fields.Float(string="Hours", related='course_id.hours')
    students_limit = fields.Integer(string="Students limit")
    expiration_days = fields.Integer(string="Expiration days", default=0)
    date_diplomas = fields.Datetime(string="Date diplomas")
    modality_id = fields.Many2one('op.modality', string='Modality',
                                  related='course_id.modality_id')
    user_company_id = fields.Integer(string="Company id",
                                     compute='_get_current_user')
    op_batch_subject_rel_ids = fields.One2many('op.batch.subject.rel',
                                               'batch_id')
    subject_count = fields.Integer(compute='_compute_subject_count')
    student_count = fields.Integer(compute='_compute_student_count')

    @api.depends()
    def _get_current_user(self):
        for rec in self:
            rec.user_company_id = self.env.user.company_id

    @api.multi
    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        for record in self:
            start_date = fields.Date.from_string(record.start_date)
            end_date = fields.Date.from_string(record.end_date)
            if start_date > end_date:
                logger.info("End Date cannot be set before Start Date.")
            #     raise ValidationError(
            #         _("End Date cannot be set before Start Date."))

    def _compute_subject_count(self):
        """Compute the number of distinct subjects linked to the batch."""
        for batch in self:
            sub_count = len(batch.course_id.subject_ids)
            batch.subject_count = sub_count

    def action_open_subjects(self):
        """Display the linked subjects and adapt the view to the number of
        records to display."""
        self.ensure_one()
        subjects = self.course_id.subject_ids
        action = \
            self.env.ref('openeducat_core.act_open_op_subject_view').read()[0]
        if len(subjects) > 1:
            action['domain'] = [('id', 'in', subjects.ids)]
        elif len(subjects) == 1:
            form_view = [(self.env.ref(
                'openeducat_core.view_op_subject_form').id, 'form')]
            if 'views' in action:
                logger.info("=== LINE 52 ===")
                action['views'] = form_view + [(state, view) for state, view in
                                               action['views'] if
                                               view != 'form']
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
        """Display the linked students and adapt the view to the number of
        records to display."""
        self.ensure_one()
        students = self.student_lines
        action = \
            self.env.ref('openeducat_core.act_open_op_student_view').read()[0]
        if len(students) > 1:
            action['domain'] = [('batch_id', 'in', students.ids)]
        elif len(students) == 1:
            form_view = [(self.env.ref(
                'openeducat_core.view_op_student_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in
                                               action['views'] if
                                               view != 'form']
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
        offset = self.search_count([])
        rows = s.get_all_courses(offset=offset)
        int_break = 0
        for batch in rows:
            course_code = str(batch.Curso_Id)
            logger.info('Curso_Id: {0}'.format(course_code))
            try:
                existent_batch = self.search([('code', '=',
                                               "{0}".format(course_code))])
                if len(existent_batch) < 1:
                    course = self.env['op.course'].search(
                        [('code', 'ilike', batch.code)], limit=1)
                    partner = self.env['res.partner'].search(
                        [('name', 'ilike', batch.Coordinador)], limit=1)
                    campus = self.env['op.campus'].search(
                        [('name', 'ilike', batch.Marca)], limit=1)
                    practices = self.env['op.practices.type'].search(
                        [('name', 'ilike', batch.TipoPracticas)], limit=1)
                    end_date = batch.FechaFin or self.add_years(
                        fields.Date.today(), 1)

                    batch_values = {
                        'name': batch.Curso_Id,
                        'code': batch.Curso_Id,
                        'course_id': course.id,
                        'start_date': batch.FechaInicio or batch.FechaAlta
                                      or fields.Date.today(),
                        'end_date': end_date,
                        'coordinator': partner.id or None,
                        'campus_id': campus.id or None,
                        'date_diplomas': batch.FechaDiplomas,
                        'academic_year': batch.AnyAcademico,
                        'days_week': batch.DiaSemana,
                        'schedule': batch.Horario,
                        'class_place': batch.LugarClase,
                        'students_limit': batch.LimiteMatriculas,
                        'type_practices': practices.id or None
                    }

                    logger.info("course: {0}".format(course))
                    if course.id:
                        res = super(OpBatch, self).create(batch_values)
                        print(res)

                if int_break == 50 and os.name != "posix":
                    break
                int_break += 1
            except Exception as e:
                logger.info(e)
                continue
        logger.info("**************************************")
        logger.info("End of script: import batches")
        logger.info("**************************************")

    @staticmethod
    def add_years(d, years):
        """Return a date that's `years` years after the date (or datetime)
        object `d`. Return the same calendar date (month and day) in the
        destination year, if it exists, otherwise use the following day
        (thus changing February 29 to March 1).
        """
        try:
            return d.replace(year=d.year + years)
        except ValueError:
            return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))
