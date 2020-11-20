# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
from requests import post

from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class Moodle(models.Model):
    _name = "moodle"

    def moodle_request(self, function, params):
        try:
            config_params = self.env['ir.config_parameter'].sudo()
            token = config_params.get_param('moodle_token')
            url = config_params.get_param('moodle_url')
            endpoint = config_params.get_param('moodle_endpoint')
            params.update({
                'wstoken': token,
                'moodlewsrestformat': 'json',
                'wsfunction': function
            })
            response = post(url + endpoint, params)
            response = response.json()

        except Exception as e:
            logger.error(e)
            # raise UserError(_("Error on moodle connection values: " % str(e)))
            response = []

        return response

    def get_last_access_cron(self):

        params = {
            'criteria[0][key]': 'confirmed',
            'criteria[0][value]': 1
        }
        response = self.moodle_request(function='core_user_get_users', params=params)
        return response['users']

    def get_last_access(self, key, value):
        params = {
            'field': key,
            'values[0]': value
        }
        response = self.moodle_request(function='core_user_get_users_by_field', params=params)
        return response