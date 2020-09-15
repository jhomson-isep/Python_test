# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
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
    period = fields.Char(string="Period")
    hours = fields.Float(string="Hours")
    credits = fields.Float(string="Credits")
    name_catalan = fields.Char(string="Catalan name")
    section = fields.Char(string="Section")
    moodle_category_id = fields.Integer(string="Moodle category Id")
    moodle_code = fields.Char(string="Moodle code", size=16)
    fees_term_id = fields.Many2one('op.fees.terms', 'Fees Term')
    level = fields.Char(string="Level", size=1)
    ects = fields.Integer("ECTS", default=0)
    acknowledgments = fields.Text("Acknowledgments", size=700)
    reconeixements = fields.Text("Reconeixements", size=700)
    content = fields.Text("Content", size=700)

    @api.model
    def create(self, values):
        logger.info("On create course")
        try:
            config_params = self.env['ir.config_parameter'].sudo()
            token = config_params.get_param('moodle_token')
            url = config_params.get_param('moodle_url')
            endpoint = config_params.get_param('moodle_endpoint')
            send_moodle = config_params.get_param('send_moodle')
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
            # try:
            #     for subject in self.subject_ids:
            #         self.create_moodle_course(subject, self.moodle_category_id)
            # except ValueError:
            #     logger.info("Error calling Moodle API\n", ValueError)

        res = super(OpCourse, self).write(values)
        return res

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

                if int_break == 50 and os.name != "posix":
                    break
                int_break += 1
            except Exception as e:
                logger.info("===== Fallo ======")
                logger.info(e)
                logger.info(course_values)
                continue
