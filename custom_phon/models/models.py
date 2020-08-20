# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import ValidationError
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

    @api.model
    def create(self, values):
        pho = super(_customphon, self).create(values)
        numero = pho.phone
        numero2 = pho.mobile

        if pho.phone and pho.mobile:
            numero = numero.replace("+", "")
            numero = numero.replace("(", "")
            numero = numero.replace(")", "")
            numero = numero.replace("-", "")
            numero = numero.replace(" ", "")
            numero2 = numero2.replace("+", "")
            numero2 = numero2.replace("(", "")
            numero2 = numero2.replace(")", "")
            numero2 = numero2.replace("-", "")
            numero2 = numero2.replace(" ", "")
            if ((numero.isdigit() == True) and (numero2.isdigit())):
                valor = len(numero)
                valor2 = len(numero2)
                numero = int(numero)
                numero2 = int(numero2)
                if (((valor >= 9) and (valor <= 15)) and ((valor2 >= 9) and (valor2 <= 15))):
                    if (valor == 10 or valor == 9) and (valor2 == 9 or valor2 == 10):
                        pho.phone = numero
                        """pho.mobile = numero2"""
                        return pho
                    if (valor > 10 and valor2 < 11):
                        numero = str(numero)
                        numero = "+" + numero
                        pho.phone = numero
                        numero2 = str(numero2)
                        """pho.mobile = numero2"""
                        return pho
                    if (valor2 > 10 and valor < 11):
                        numero2 = str(numero2)
                        numero2 = "+" + numero2
                        numero = str(numero)
                        pho.phone = numero
                        """pho.mobile = numero2"""
                        return pho
                else:
                    raise ValidationError("Numero telefónico o móvil en formato incorrecto")
            else:
                raise ValidationError("Número telefónico o móvil en formato incorrecto")

        elif (pho.phone and pho.mobile == False):
            numero = numero.replace("+", "")
            numero = numero.replace("(", "")
            numero = numero.replace(")", "")
            numero = numero.replace("-", "")
            numero = numero.replace(" ", "")
            if numero.isdigit() == True:
                valor = len(numero)
                numero = int(numero)
                if ((valor >= 9) and (valor<=15)):
                    if (valor == 10 or valor == 9):
                        pho.phone = numero
                        return pho
                    if valor > 10:
                        numero = str(numero)
                        numero = "+" + numero
                        pho.phone = numero
                        return pho
                else:
                    raise ValidationError("Numero telefónico en formato incorrecto")
            else:
                raise ValidationError("Número telefónico en formato incorrecto")
        elif (pho.mobile and pho.phone == False):
            numero2 = numero2.replace("+", "")
            numero2 = numero2.replace("(", "")
            numero2 = numero2.replace(")", "")
            numero2 = numero2.replace("-", "")
            numero2 = numero2.replace(" ", "")
            if numero2.isdigit() == True:
                valor = len(numero2)
                numero2 = int(numero2)
                if ((valor >= 9) and (valor <= 15)):
                    if (valor == 10 or valor == 9):
                        pho.phone = numero2
                        return pho
                    if valor > 10:
                        numero2 = str(numero2)
                        numero2 = "+" + numero2
                        pho.phone = numero2
                        return pho
                else:
                    raise ValidationError("Numero móvil en formato incorrecto")
            else:
                raise ValidationError("Número móvil en formato incorrecto")
        else:
            raise ValidationError("Introduzca un número de teléfono, ya sea móvil o fijo")

    @api.multi
    def write(self, values):
        pho = super(_customphon, self).write(values)
        for sel in self:
            sel.phone
        return pho