# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from requests import get, post
from .op_sql import SQL
import logging
import os

logger = logging.getLogger(__name__)


class OpSubject(models.Model):
    _inherit = 'op.subject'
    sepyc_code = fields.Char(string="SEPYC code", size=16)
    moodle_course_id = fields.Integer(string='Moodle course Id')
    uvic_code = fields.Char(string="UVIC code", size=16)

    @api.model
    def create(self, values):
        logger.info("On create subject")
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
                'courses[0][fullname]': values.name,
                'courses[0][shortname]': values.code,
                'courses[0][idnumber]': values.code,
                'courses[0][summary]': values.name,
                'courses[0][format]': 'topics',
                'courses[0][visible]': 1,
                'courses[0][lang]': 'en',
                # 'courses[0][categoryid]': category,
                "wstoken": token,
                'moodlewsrestformat': 'json',
                "wsfunction": 'core_course_create_courses'
            }

            try:
                response = post(url + endpoint, params)
                response = response.json()
                logger.info(response)
                if type(response) == dict and response.get('exception'):
                    logger.info(response.get('message'))
                else:
                    values.update({'moodle_course_id': response[0].get('id')})
            except Exception:
                logger.info("Error calling Moodle API\n", Exception)

        res = super(OpSubject, self).create(values)
        return res

    @api.multi
    def write(self, values):
        logger.info("On update subject")
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
                'categories[0][id]': self.moodle_course_id,
                'courses[0][fullname]': values.name,
                'courses[0][shortname]': values.code,
                'courses[0][idnumber]': values.code,
                'courses[0][summary]': values.name,
                "wstoken": token,
                'moodlewsrestformat': 'json',
                "wsfunction": 'core_course_update_courses'
            }

            try:
                logger.info(self.moodle_category_id)
                response = post(url + endpoint, params)
                response = response.json()
                logger.info(response)
                if type(response) == dict and response.get('exception'):
                    logger.info("Error calling Moodle API\n", response)
            except ValueError:
                logger.info("Error calling Moodle API\n", ValueError)

        res = super(OpSubject, self).write(values)
        return res

    def import_subjects(self):
        s = SQL()
        logger.info("**************************************")
        logger.info("import subjects")
        logger.info("**************************************")
        rows = s.get_all_subjects()
        int_break = 0
        for subject in rows:
            existent_subject = self.search([('code', '=', subject.CodAsignatura)])
            if len(existent_subject) < 1:
                try:
                    subject_values = {
                        'name': subject.NomAsignatura,
                        'code': subject.CodAsignatura,
                        'type': 'theory',
                        'subject_type': 'compulsory',
                        'uvic_code': subject.CodUvic,
                        'moodle_course_id': subject.Moodle
                    }

                    res = super(OpSubject, self).create(subject_values)
                    print(res)

                    if int_break == 50 and os.name != "posix":
                        break
                    int_break += 1
                except Exception as e:
                    logger.info(e)
                    continue
