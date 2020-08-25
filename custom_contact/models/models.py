# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import UserError
import re


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

class _Customfield(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        correo = values.get('email')
        if correo:
            if re.match('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$', str(correo).lower()):
                direccion, dominio = correo.split("@")
                if dominio == "gmali.com":
                    dominio = "gmail.com"
                    correo = ""
                    correo = direccion
                elif dominio == "gmial.com":
                    dominio = "gmail.com"
                    correo = ""
                    correo = direccion
                elif dominio == "gmail.cm":
                    dominio = "gmail.com"
                    correo = ""
                    correo = direccion
                elif dominio == "gmal.com":
                    dominio = "gmail.com"
                    correo = ""
                    correo = direccion
                elif dominio == "gmil.com":
                    dominio = "gmail.com"
                    correo = ""
                    correo = direccion
                elif dominio == "hotmal.com":
                    dominio = "hotmail.com"
                    correo = ""
                    correo = direccion
                elif dominio == "hotmial.com":
                    dominio = "hotmail.com"
                    correo = ""
                    correo = direccion
                elif dominio == "jotmail.com":
                    dominio = "hotmail.com"
                    correo = ""
                    correo = direccion
                elif dominio == "hotmali.com":
                    dominio = "hotmail.com"
                    correo = ""
                    correo = direccion
                elif dominio == "hotmail.cm":
                    dominio = "hotmail.com"
                    correo = ""
                    correo = direccion
                elif dominio == "hotmal.es":
                    dominio = "hotmail.es"
                    correo = ""
                    correo = direccion
                elif dominio == "hotmial.es":
                    dominio = "hotmail.es"
                    correo = ""
                    correo = direccion
                elif dominio == "jotmail.es":
                    dominio = "hotmail.es"
                    correo = ""
                    correo = direccion
                elif dominio == "hotmali.es":
                    dominio = "hotmail.es"
                    correo = ""
                    correo = direccion
                elif dominio == "outlok.es":
                    dominio = "outlook.es"
                    correo = ""
                    correo = direccion
                elif dominio == "outlock.es":
                    dominio = "outlook.es"
                    correo = ""
                    correo = direccion
                elif dominio == "outloc.es":
                    dominio = "outlook.es"
                    correo = ""
                    correo = direccion
                elif dominio == "oulook.es":
                    dominio = "outlook.es"
                    correo = ""
                    correo = direccion
                elif dominio == "outlok.com":
                    dominio = "outlook.com"
                    correo = ""
                    correo = direccion
                elif dominio == "outlock.com":
                    dominio = "outlook.com"
                    correo = ""
                    correo = direccion
                elif dominio == "outloc.com":
                    dominio = "outlook.com"
                    correo = ""
                    correo = direccion
                elif dominio == "oulook.com":
                    dominio = "outlook.com"
                    correo = ""
                    correo = direccion
                elif dominio == "outlook.cm":
                    dominio = "outlook.com"
                    correo = ""
                    correo = direccion
                elif dominio == "yaho.com":
                    dominio = "yahoo.com"
                    correo = ""
                    correo = direccion
                elif dominio == "yajoo.com":
                    dominio = "yahoo.com"
                    correo = ""
                    correo = direccion
                elif dominio == "jahoo.com":
                    dominio = "yahoo.com"
                    correo = ""
                    correo = direccion
                elif dominio == "yahoo.cm":
                    dominio = "yahoo.com"
                    correo = ""
                    correo = direccion
                elif dominio == "yaho.es":
                    dominio = "yahoo.es"
                    correo = ""
                    correo = direccion
                elif dominio == "yajoo.es":
                    dominio = "yahoo.es"
                    correo = ""
                    correo = direccion
                elif dominio == "jahoo.es":
                    dominio = "yahoo.es"
                    correo = ""
                    correo = direccion
                correo = direccion + '@' + dominio
                values.update({'email': correo})
                res = super(_Customfield, self).create(values)
                return res
            else:
                raise UserError("Formato de correo no válido")
        elif not correo:
            raise UserError('Introduzca una dirección de correo electrónico')

    @api.multi
    def write(self, values):
        res = super(_Customfield, self).write(values)
        return res

    """@staticmethod
    def es_correo_valido(correo):
        if re.match('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$', str(correo).lower()):
            direccion, dominio = correo.split("@")
            if dominio == "gmali.com":
                dominio = "gmail.com"
                correo = ""
                correo = direccion
            correo = direccion + '@' + dominio
            return correo
        else:
            raise UserError("Dirección de correo en formato no válido")"""
