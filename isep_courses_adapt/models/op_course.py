# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from requests import get, post
from ast import literal_eval
import logging

logger = logging.getLogger(__name__)


# TOKEN = "3de3ace98f80a5b1e16c84a378d72741"
# URL = "https://isep.moodlecloud.com"
# ENDPOINT = "/webservice/rest/server.php"


class OpCourse(models.Model):
    _inherit = 'op.course'

    product_template_id = fields.Many2one('product.template', string='Producto')
    # code_product = fields.Char(related='product_template_id.default_code', string='Codigo de Producto')

    modality_id = fields.Many2one('op.modalidad', string='Modality')
    evaluation_type_id = fields.Many2one('op.evaluation.type', string='Evaluation type')
    period = fields.Char(string="Period")
    hours = fields.Float(string="Hours")
    credits = fields.Float(string="Credits")
    name_catalan = fields.Char(string="Catalan name")
    section = fields.Char(string="Section")
    moodle_category_id = fields.Integer(string="Moodle category Id")
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
            logger.error(config_params)
            token = config_params.get_param('moodle_token')
            url = config_params.get_param('moodle_url')
            endpoint = config_params.get_param('moodle_endpoint')
        except Exception as e:
            raise UserError(_("Error on moddle conection: " % str(e)))
            logger.error(e)

        params = {
            'categories[0][name]': values.get('name'),
            'categories[0][parent]': 0,
            'wstoken': token,
            'moodlewsrestformat': 'json',
            'wsfunction': 'core_course_create_categories'
        }
        if values.get('parent_id'):
            params.update({'categories[0][parent]': values.get('parent_id')})
        try:
            response = post(url + endpoint, params)
            response = response.json()
            logger.info(response)
            if type(response) == dict and response.get('exception'):
                logger.info(response.get('exception'))
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
            logger.error(config_params)
            token = config_params.get_param('moodle_token')
            url = config_params.get_param('moodle_url')
            endpoint = config_params.get_param('moodle_endpoint')
        except Exception as e:
            logger.error(str(e))
            Warning(_("Error on moddle conection: " % str(e)))
        params = {
            'categories[0][id]': self.moodle_category_id,
            'categories[0][name]': values.get('name'),
            "wstoken": token,
            'moodlewsrestformat': 'json',
            "wsfunction": 'core_course_update_categories'
        }
        if values.get('parent_id') or self.parent_id:
            params.update({'categories[0][parent]': self.parent_id.moodle_category_id})
        try:
            logger.info(self.moodle_category_id)
            response = post(url + endpoint, params)
            response = response.json()
            logger.info(response)
            if type(response) == dict and response.get('exception'):
                logger.info("Error calling Moodle API\n", response)
        except ValueError:
            logger.info("Error calling Moodle API\n", ValueError)
        res = super(OpCourse, self).write(values)
        try:
            for subject in self.subject_ids:
                self.create_moodle_course(subject, self.moodle_category_id)
        except ValueError:
            logger.info("Error calling Moodle API\n", ValueError)
        return res

    def create_moodle_course(self, subject, category):
        try:
            config_params = self.env['ir.config_parameter'].sudo()
            token = config_params.get_param('moodle_token')
            url = config_params.get_param('moodle_url')
            endpoint = config_params.get_param('moodle_endpoint')
        except Exception as e:
            logger.error(str(e))
            Warning(_("Error on moddle conection: " % str(e)))
        params = {
            'courses[0][fullname]': subject.name,
            'courses[0][shortname]': subject.code,
            'courses[0][idnumber]': subject.code,
            'courses[0][summary]': subject.name,
            'courses[0][format]': 'topics',
            'courses[0][visible]': 1,
            'courses[0][lang]': 'en',
            'courses[0][categoryid]': category,
            "wstoken": token,
            'moodlewsrestformat': 'json',
            "wsfunction": 'core_course_create_courses'
        }
        try:
            logger.info(category)
            response = post(url + endpoint, params)
            response = response.json()
            logger.info(response)
            if type(response) == dict and response.get('exception'):
                logger.info(response.get('exception'))
            else:
                self.env['op.subject'].write({'id': subject.id, 'moodle_course_id': response[0].get('id')})
        except Exception:
            logger.info("Error calling Moodle API\n", Exception)
