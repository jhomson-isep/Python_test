# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import UserError
import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        email = values.get('email')
        if email:
            email = self.check_email(email)
            values.update({'email': email})
        # else:
        #     raise UserError('Introduzca una dirección de correo electrónico')

        res = super(ResPartner, self).create(values)
        return res

    @api.multi
    def write(self, values):
        email = values.get('email')
        if email:
            email = self.check_email(email)
            values.update({'email': email})
        res = super(ResPartner, self).write(values)
        return res

    @staticmethod
    def check_email(email):
        gmail = ['gmali.com', 'gmial.com', 'gmail.cm', 'gmal.com', 'gmil.com']
        hotmail = ['hotmal.com', 'hotmail.com.mx', 'hotmai.com',
                   'hotmial.com', 'jotmail.com', 'hotmali.com',
                   'hotmail.cm', 'hormail.com']
        hotmail_es = ['hotmal.es', 'hotmai.es', 'hotmial.es', 'hormail.es'
                      'jotmail.es', 'hotmali.es', 'hotmail.es']
        outlook = ['outlok.com', 'outlock.com', 'outloc.com', 'oulook.com',
                   'oulook.com', 'otlook.com', 'outluk.com']
        outlook_es = ['outlok.es', 'outlock.es', 'outloc.es', 'oulook.es',
                      'oulook.es', 'otlook.es', 'outluk.es']
        yahoo = ['yaho.com', 'yajoo.com', 'jahoo.com', 'yahoo.cm']
        yahoo_es = ['yaho.es', 'yajoo.es', 'jahoo.es']
        if re.match('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$',
                    str(email).lower()):
            address, domain = email.split("@")

            if domain in gmail:
                domain = 'gmail.com'
            if domain in hotmail:
                domain = 'hotmail.com'
            if domain in hotmail_es:
                domain = 'hotmail.es'
            if domain in outlook:
                domain = 'outlook.com'
            if domain in outlook_es:
                domain = 'outlook.es'
            if domain in yahoo:
                domain = 'yahoo.com'
            if domain in yahoo_es:
                domain = 'yahoo.es'
        else:
            raise UserError("Invalid format code")

        email = address + '@' + domain
        return email
