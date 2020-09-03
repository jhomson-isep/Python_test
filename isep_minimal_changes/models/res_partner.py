from odoo import models, fields, api, _
import logging

class ResPartner(models.Model):
    _inherit = 'res.partner'

    actual_campaign = fields.Many2many('utm.campaign', string="Campaña Actual")