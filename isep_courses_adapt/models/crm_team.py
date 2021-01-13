# -*- coding: utf-8 -*-

from odoo import models, fields
import logging

logger = logging.getLogger(__name__)


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    campus_id = fields.Many2one(comodel_name='op.campus', string='Campus')
