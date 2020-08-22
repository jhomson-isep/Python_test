# -*- coding: utf-8 -*-

from odoo import models, api
from odoo.exceptions import UserError
import logging
import re

logger = logging.getLogger(__name__)


class _customphon(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        tel = values.get('phone')
        mov = values.get('mobile')
        if tel:
            tel = self._checkphones(tel)
            values.update({'phone': tel})
        if mov:
            mov = self._checkphones(mov)
            values.update({'mobile': mov})
        if not tel and not mov:
            raise UserError("Introduzca un número telefónico o número móvil por favor")
        values.update({'phone': tel, 'mobile': mov})
        res = super(_customphon, self).create(values)
        return res

    def write(self, values):
        tel = values.get('phone')
        mov = values.get('mobile')
        if tel or mov:
            if tel:
                tel = self._checkphones(tel)
                values.update({'phone': tel})
            if mov:
                mov = self._checkphones(mov)
                values.update({'mobile': mov})
            logger.info("tel: ".format(tel))
            logger.info("mov: ".format(mov))
            values.update({'phone': tel, 'mobile': mov})
        res = super(_customphon, self).write(values)
        if not self.mobile and not self.phone:
            raise UserError("Introduzca un número telefónico o número móvil por favor")
        return res

    def _checkphones(self, numero):
        numero = self.clear_phone(numero)
        logger.info(numero)
        if numero.isdigit():
            valor = len(numero)
            if valor >= 9 and valor <= 15:
                if valor > 10:
                    numero = "+" + numero
                return numero
            else:
                raise UserError("Numero telefónico en formato incorrecto")
        else:
            raise UserError("Número telefónico en formato incorrecto")

    @staticmethod
    def clear_phone(phone):
        for ch in ['+', '(', ')', '-', ' ', '/']:
            if ch in phone:
                phone = phone.replace(ch, "")
        return phone
