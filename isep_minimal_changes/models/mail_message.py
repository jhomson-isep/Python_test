# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request


class MailMessage(models.Model):
    _inherit = 'mail.message'

    source = fields.Char(string='source')

    @api.model
    def create(self, values):
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        values.update({'source': ip})
        res = super(MailMessage, self).create(values)
        return res












