# -*- coding: utf-8 -*-

from odoo import models, fields, api

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

class _customname(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        dat = super(_customname, self).create(values)
        nombre = dat.name
        if nombre.istitle():
            dat.name = nombre
            return dat
        else:
            dat.name = nombre.title()
        return dat

    @api.multi
    def write(self,values):
        dat = super(_customname, self).write(values)
        for sel in self:
            sel.name
        return