# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import UserError


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

class _Customphon(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        tel = values.get('phone')
        mov = values.get('mobile')
        if tel and mov:
            tel = self._checkphones(tel)
            mov = self._checkphones(mov)
            values.update({'phone': tel, 'mobile': mov})
            res = super(_Customphon, self).create(values)
            return res
        elif tel and mov is False:
            tel = self._checkphones(tel)
            values.update({'phone': tel, 'mobile': mov})
            res = super(_Customphon, self).create(values)
            return res
        elif tel is False and mov:
            mov = self._checkphones(mov)
            values.update({'phone': tel, 'mobile': mov})
            res = super(_Customphon, self).create(values)
            return res
        elif tel is False and mov is False:
            raise UserError("Introduzca un número telefónico o número móvil por favor")

    @api.multi
    def write(self, vals):
        res = super(_Customphon, self).write(vals)
        return res

    @staticmethod
    def _checkphones(numero):
        numero = numero.replace("+", "")
        numero = numero.replace("(", "")
        numero = numero.replace(")", "")
        numero = numero.replace("-", "")
        numero = numero.replace(" ", "")
        if numero.isdigit() is True:
            valor = len(numero)
            if (valor >= 9) and (valor <= 15):
                if valor > 10:
                    numero = "+" + numero
                return numero
            else:
                raise UserError("Numero telefónico en formato incorrecto")
        else:
            raise UserError("Número telefónico en formato incorrecto")
