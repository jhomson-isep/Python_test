# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    actual_campaign = fields.Many2many('utm.campaign', string="Campaña Actual")
    # is_programmer = fields.Boolean(string="Programmer", default=False)
