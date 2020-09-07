# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        phone = values.get('phone')
        mobile = values.get('mobile')
        if phone and mobile:
            phone = self.check_phone(phone)
            mobile = self.check_phone(mobile)
            values.update({'phone': phone, 'mobile': mobile})
        elif phone and mobile is False:
            phone = self.check_phone(phone)
            values.update({'phone': phone, 'mobile': mobile})
        elif phone is False and mobile:
            mobile = self.check_phone(mobile)
            values.update({'phone': phone, 'mobile': mobile})
        res = super(ResPartner, self).create(values)
        return res

    @staticmethod
    def check_phone(number):
        number = number.replace("+", "")
        number = number.replace("(", "")
        number = number.replace(")", "")
        number = number.replace("-", "")
        number = number.replace(" ", "")
        if number.isdigit() is True:
            valor = len(number)
            if (valor >= 9) and (valor <= 15):
                if valor > 10:
                    number = "+" + number
                return number
            else:
                raise UserError("Numero telefónico en formato incorrecto")
        else:
            raise UserError("Número telefónico en formato incorrecto")
