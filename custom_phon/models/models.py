# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import UserError
import re

# class custom_phon(models.Model):
#     _name = 'custom_phon.custom_phon'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class _customphon(models.Model):
    _inherit = 'res.partner'

    def _checkphones(self, numero):
            numero = numero.replace("+", "")
            numero = numero.replace("(", "")
            numero = numero.replace(")", "")
            numero = numero.replace("-", "")
            numero = numero.replace(" ", "")
            numero = numero.replace("/", "")
            if (numero.isdigit() == True):
                valor = len(numero)
                if ((valor >= 9) and (valor <= 15)):
                    if (valor > 10):
                        numero = "+" + numero
                    return numero
                else:
                    raise UserError("Numero telefónico en formato incorrecto")
            else:
                raise UserError("Número telefónico en formato incorrecto")

    @api.model
    def create(self, values):
        tel = values.get('phone')
        mov = values.get('mobile')
        if tel and mov:
            tel = self._checkphones(tel)
            mov = self._checkphones(mov)
            values.update({'phone': tel, 'mobile': mov})
            res = super(_customphon, self).create(values)
            return res
        elif tel and mov == False:
            tel = self._checkphones(tel)
            values.update({'phone': tel, 'mobile': mov})
            res = super(_customphon, self).create(values)
            return res
        elif tel == False and mov:
            mov = self._checkphones(mov)
            values.update({'phone': tel, 'mobile': mov})
            res = super(_customphon, self).create(values)
            return res
        elif tel == False and mov == False:
            raise UserError("Introduzca un número telefónico o número móvil por favor")


    def write(self, values):
        tel2 = values.get('phone')
        mov2 = values.get('mobile')
        if tel2 and mov2:
            tel2 = self._checkphones(tel2)
            mov2 = self._checkphones(mov2)
            values.update({'phone': tel2, 'mobile': mov2})
            res = super(_customphon, self).write(values)
            return res
        elif tel2 and mov2 == False:
            tel = self._checkphones(tel2)
            values.update({'phone': tel2, 'mobile': mov2})
            res = super(_customphon, self).write(values)
            return res
        elif tel2 == False and mov2:
            mov = self._checkphones(mov2)
            values.update({'phone': tel2, 'mobile': mov2})
            res = super(_customphon, self).write(values)
            return res
        elif tel2 == False and mov2 == False:
            raise UserError("Introduzca un número telefónico o número móvil por favor")
