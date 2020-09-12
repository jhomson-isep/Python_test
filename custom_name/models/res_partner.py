# -*- coding: utf-8 -*-

from odoo import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        name = values.get('name')
        if name and not name.istitle():
            name = self.set_name(name)
            values.update({'name': name})
        res = super(ResPartner, self).create(values)
        return res

    @api.multi
    def write(self, values):
        name = values.get('name')
        if name and not name.istitle():
            name = self.set_name(name)
            values.update({'name': name})
        res = super(ResPartner, self).write(values)
        return res

    @staticmethod
    def set_name(name):
        return name.title()
