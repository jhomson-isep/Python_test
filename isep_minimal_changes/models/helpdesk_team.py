# -*- coding: utf-8 -*-
from odoo import models, fields


class HelpDeskTeam(models.Model):
    _inherit = 'helpdesk.team'
    ticket_notify = fields.Many2many('res.partner',
                                     string="Notificar a:")
