# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging, re

_logger = logging.getLogger(__name__)
# class extra-addons/custom_contact(models.Model):
#     _name = 'extra-addons/custom_contact.extra-addons/custom_contact'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class customfield(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        datos = super(customfield, self).create(values)
        correo = datos.email
        if re.match('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$', str(correo).lower()):
            direccion, dominio = correo.split("@")
            direccion = direccion.lower()
            if dominio == "gmali.com":
                dominio = "gmail.com"
                correo = ""
                correo = direccion
            elif dominio == 'gmal.com':
                dominio = "gmail.com"
                correo = ""
                correo = direccion
            elif dominio == 'gmial.com':
                dominio = "gmail.com"
                correo = ""
                correo = direccion
            elif dominio == 'outlock.com':
                dominio = "outlook.com"
                correo = ""
                correo = direccion
            elif dominio == 'olook.com':
                dominio = "outlook.com"
                correo = ""
                correo = direccion
            elif dominio == 'otlook.com':
                dominio = "outlook.com"
                correo = ""
                correo = direccion
            elif dominio == 'outlooc.com':
                dominio = "outlook.com"
                correo = ""
                correo = direccion
            elif dominio == 'outlok.com':
                dominio = "outlook.com"
                correo = ""
                correo = direccion
            elif dominio == 'hotmali.com':
                dominio = "hotmail.com"
                correo = ""
                correo = direccion
            elif dominio == 'jotmail.com':
                dominio = "hotmail.com"
                correo = ""
                correo = direccion
            elif dominio == 'hotmal.com':
                dominio = "hotmail.com"
                correo = ""
                correo = direccion
            elif dominio == 'ohomtmal.com':
                dominio = "hotmail.com"
                correo = ""
                correo = direccion
            elif dominio == 'jahoo.com':
                dominio = "yahoo.com"
                correo = ""
                correo = direccion
            elif dominio == 'jaho.com':
                dominio = "yahoo.com"
                correo = ""
                correo = direccion
            elif dominio == 'yaho.com':
                dominio = "yahoo.com"
                correo = ""
                correo = direccion
            elif dominio == 'yajoo.com':
                dominio = "yahoo.com"
                correo = ""
                correo = direccion
            elif dominio == 'yajo.com':
                dominio = "yahoo.com"
                correo = ""
                correo = direccion
            elif dominio == 'coud.com':
                dominio = "icloud.com"
                correo = ""
                correo = direccion
            elif dominio == 'iclau.com':
                dominio = "icloud.com"
                correo = ""
                correo = direccion
            elif dominio == 'iclou.com':
                dominio = "icloud.com"
                correo = ""
                correo = direccion
            elif dominio == 'iclud.com':
                dominio = "icloud.com"
                correo = ""
                correo = direccion
            elif dominio == 'al.com':
                dominio = "aol.com"
                correo = ""
                correo = direccion
            elif dominio == 'oal.com':
                dominio = "aol.com"
                correo = ""
                correo = direccion
            elif dominio == 'ao.com':
                dominio = "aol.com"
                correo = ""
                correo = direccion
            correo = direccion + '@' + dominio
            datos.email = correo
            return datos
        else:
            raise ValidationError("Formato de correo no válido, Favor de verificar la dirección de correo")

    @api.multi
    def write(self, values):
        datos = super(customfield, self).write(values)
        for sel in self:
            sel.email
        return datos















