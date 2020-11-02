# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
from requests import post

from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class Moodle(models.Model):
    # def moodle_request(self, function, params):
    #     try:
    #         config_params = self.env['ir.config_parameter'].sudo()
    #         token = config_params.get_param('moodle_token')
    #         url = config_params.get_param('moodle_url')
    #         endpoint = config_params.get_param('moodle_endpoint')
    #     except Exception as e:
    #         logger.error(e)
    #         raise UserError(_("Error on moodle connection values: " % str(e)))
    #
    #     params.update({
    #         'wstoken': token,
    #         'moodlewsrestformat': 'json',
    #         'wsfunction': function
    #     })
    #     response = post(url + endpoint, params)
    #     response = response.json()
    #
    #     return response