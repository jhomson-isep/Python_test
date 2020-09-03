from odoo import models, fields, api, _
import logging

class ResPartner(models.model):
    _inherit = 'res.partner'

    actual_campaign = fields.Many2many('res.partner', string="Campaña Actual")