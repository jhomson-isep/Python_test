# -*- coding: utf-8 -*-

from odoo import models, api


# class custom_name(models.Model):
#     _name = 'custom_name.custom_name'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class _Customname(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        nombre = values.get('name')
        if nombre and not nombre.istitle():
            nombre = self._checkname(nombre)
            values.update({'name': nombre})
        res = super(_Customname, self).create(values)
        return res

    @api.multi
    def write(self, values):
        nombre = values.get('name')
        if nombre and not nombre.istitle():
            nombre = self._checkname(nombre)
            values.update({'name': nombre})
        res = super(_Customname, self).write(values)
        return res

    @staticmethod
    def _checkname(nombre):
        nombre = nombre.title()
        return nombre
