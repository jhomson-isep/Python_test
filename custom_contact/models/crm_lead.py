# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import UserError
import re


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, values):
        email = values.get('email_from')
        name = values.get('name')
        if email:
            email = self.check_email(email)
            if values.get('email_from') in name:
                name = name.replace(values.get('email_from'), email)
            values.update({'email_from': email, 'name': name})
        res = super(CrmLead, self).create(values)
        return res

    @staticmethod
    def check_email(email):
        gmail = ['gmali.com', 'gmial.com', 'gmail.cm', 'gmal.com', 'gmil.com']
        hotmail = ['hotmal.com', 'hotmail.com.mx', 'hotmai.com',
                   'hotmial.com', 'jotmail.com', 'hotmali.com', 'hotmail.cm',
                   'hotmail.cim', 'hormail.com']
        hotmail_es = ['hotmal.es', 'hotmai.es', 'hotmial.es',
                      'jotmail.es', 'hotmali.es', 'hotmail.es']
        outlook = ['outlok.com', 'outlock.com', 'outloc.com', 'oulook.com',
                   'oulook.com', 'otlook.com', 'outluk.com', 'outlook.cim',
                   'outlook.cpm', 'outlook.cum']
        outlook_es = ['outlok.es', 'outlock.es', 'outloc.es', 'oulook.es',
                      'oulook.es', 'otlook.es', 'outluk.es']
        yahoo = ['yaho.com', 'yajoo.com', 'jahoo.com', 'yahoo.cm', 'yahoo.cim',
                 'yahoo.cpm', 'yahoo.cum']
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
