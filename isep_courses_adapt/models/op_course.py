# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from requests import get, post
from .op_sql import SQL
import logging
import os

logger = logging.getLogger(__name__)


# TOKEN = "3de3ace98f80a5b1e16c84a378d72741"
# URL = "https://isep.moodlecloud.com"
# ENDPOINT = "/webservice/rest/server.php"


class OpCourse(models.Model):
    _inherit = 'op.course'

    product_template_id = fields.Many2one('product.template',
                                          string='Producto')
    modality_id = fields.Many2one('op.modality', string='Modality')
    evaluation_type_id = fields.Many2one('op.evaluation.type',
                                         string='Evaluation type')
    hours = fields.Float(string="Hours")
    credits = fields.Float(string="Credits")
    hp_total = fields.Float(string="Practical Hours Total", compute='_compute_hours_course')
    hi_total = fields.Float(string="Independent Hours Total", compute='_compute_hours_course')
    ht_total = fields.Float(string="Theoretical Hours Total", compute='_compute_hours_course')
    hours_total = fields.Float(string="Hours Total", compute='_compute_hours_total_course')
    credits_hp = fields.Float(string="Practical Hours Credits", compute='_compute_credits_by_hours')
    credits_hi = fields.Float(string="Independent Hours Credits", compute='_compute_credits_by_hours')
    credits_ht = fields.Float(string="Theoretical Hours Credits", compute='_compute_credits_by_hours')
    credits_total = fields.Float(string="Credits Total", compute='_compute_credits_total_course')
    uvic_program = fields.Boolean(string='UVIC program', default=False)
    sepyc_program = fields.Boolean(string='SEPYC program', default=False)
    name_catalan = fields.Char(string="Catalan name")
    section = fields.Many2one('op.section.course',
                              string='Section')
    period = fields.Many2one('op.period.course',
                              string='Period')
    moodle_category_id = fields.Integer(string="Moodle category Id")
    moodle_code = fields.Char(string="Moodle code", size=16)
    fees_term_id = fields.Many2one('op.fees.terms', 'Fees Term')
    level = fields.Char(string="Level", size=1)
    ects = fields.Integer("ECTS", default=0)
    acknowledgments = fields.Text("Acknowledgments", size=700)
    reconeixements = fields.Text("Reconeixements", size=700)
    content = fields.Text("Content", size=700)
    area_id = fields.Many2one('op.area.course', "Area of Course")

    _sql_constraints = [('unique_course_code',
                         'check(1=1)', 'Delete constrian unique code per course!')]

    @api.depends('subject_ids')
    def _compute_hours_course(self):
        self.hp_total = sum(subject.hp for subject in self.subject_ids)
        self.hi_total = sum(subject.hi for subject in self.subject_ids)
        self.ht_total = sum(subject.ht for subject in self.subject_ids)

    def _compute_credits_by_hours(self):
        min_hours_study_by_credit = 16
        self.credits_hp = self.hp_total / min_hours_study_by_credit
        self.credits_hi = self.hi_total / min_hours_study_by_credit
        self.credits_ht = self.ht_total / min_hours_study_by_credit

    def _compute_hours_total_course(self):
        self.hours_total = self.ht_total + self.hi_total + self.hp_total

    def _compute_credits_total_course(self):
        self.credits_total = self.credits_ht + self.credits_hi + self.credits_hp

    @api.model
    def create(self, values):
        logger.info("On create course")
        try:
            config_params = self.env['ir.config_parameter'].sudo()
            token = config_params.get_param('moodle_token')
            url = config_params.get_param('moodle_url')
            endpoint = config_params.get_param('moodle_endpoint')
            send_moodle = config_params.get_param('send_moodle')
            send_moodle = False
        except Exception as e:
            logger.error(e)
            raise UserError(_("Error on moodle connection values: " % str(e)))

        if send_moodle:
            params = {
                'categories[0][name]': values.get('name'),
                'categories[0][parent]': 0,
                'wstoken': token,
                'moodlewsrestformat': 'json',
                'wsfunction': 'core_course_create_categories'
            }

            if values.get('parent_id'):
                params.update({'categories[0][parent]': values.get(
                    'parent_id')})
            try:
                response = post(url + endpoint, params)
                response = response.json()
                logger.info(response)
                if type(response) == dict and response.get('exception'):
                    logger.info(response.get('message'))
                else:
                    values.update({'moodle_category_id': response[0].get('id')})
            except Exception:
                logger.info("Error calling Moodle API\n", Exception)

        res = super(OpCourse, self).create(values)
        return res

    @api.multi
    def write(self, values):
        logger.info("On update course")
        try:
            config_params = self.env['ir.config_parameter'].sudo()
            token = config_params.get_param('moodle_token')
            url = config_params.get_param('moodle_url')
            endpoint = config_params.get_param('moodle_endpoint')
            send_moodle = config_params.get_param('send_moodle')
            send_moodle = False
        except Exception as e:
            logger.error(e)
            raise UserError(_("Error on moodle connection values: " % str(e)))

        if send_moodle:
            params = {
                'categories[0][id]': self.moodle_category_id,
                'categories[0][name]': values.get('name'),
                "wstoken": token,
                'moodlewsrestformat': 'json',
                "wsfunction": 'core_course_update_categories'
            }
            if values.get('parent_id') or self.parent_id:
                params.update(
                    {'categories[0][parent]': self.parent_id.moodle_category_id})
            try:
                logger.info(self.moodle_category_id)
                response = post(url + endpoint, params)
                response = response.json()
                logger.info(response)
                if type(response) == dict and response.get('exception'):
                    logger.info("Error calling Moodle API\n", response)
            except ValueError:
                logger.info("Error calling Moodle API\n", ValueError)
            try:
                for subject in self.subject_ids:
                    self.create_moodle_course(subject, self.moodle_category_id)
            except ValueError:
                logger.info("Error calling Moodle API\n", ValueError)

        res = super(OpCourse, self).write(values)
        return res


    @api.one
    @api.constrains('area_id', 'code')
    def _check_code_area(self):
        res = self.search([('area_id', '=', self.area_id.id), ('code', '=', self.code)], limit=1)
        if res.id:
            raise ValidationError(_('One code and area for course!'))


    def import_courses(self):
        s = SQL()
        logger.info("**************************************")
        logger.info("import courses")
        logger.info("**************************************")
        rows = s.get_distinct_courses()
        int_break = 0
        for row in rows:
            try:
                default_code = row[0]
                course = self.search([('code', '=', default_code)])
                if len(course) < 1:
                    course_moodle = s.get_course_by_code(default_code)
                    logger.info(course_moodle.NombreCurso)
                    evaluation_type = self.env['op.evaluation.type'].search(
                        [('name', 'ilike', 'normal')], limit=1)
                    modality = self.env['op.modality'].search(
                        [('code', '=', course_moodle.Modalidad)], limit=1)
                    product = self.env['product.template'].search(
                        [('default_code', '=', default_code), ('active',
                                                               '=', True)],
                        limit=1)
                    logger.info(product.name)
                    course_values = {
                        'name': course_moodle.NombreCurso,
                        'code': default_code,
                        'product_template_id': product.id or None,
                        'name_catalan': course_moodle.TitolCat,
                        'evaluation_type_id': evaluation_type.id or None,
                        'modality_id': modality.id or None,
                        'hours': course_moodle.TotalHoras,
                        'credits': course_moodle.TotalCreditos,
                        'ects': course_moodle.ECTS,
                        'acknowledgments': course_moodle.Reconocimientos,
                        'reconeixements': course_moodle.Reconeixements,
                        'content': course_moodle.Contenido,
                        'moodle_code': course_moodle.MoodleId
                    }
                    if course_moodle.NombreCurso:
                        res = super(OpCourse, self).create(course_values)
                        print(res)

                # if int_break == 50 and os.name != "posix":
                #     break
                # int_break += 1
            except Exception as e:
                logger.info("===== Fallo ======")
                logger.info(e)
                logger.info(course_values)
                continue
