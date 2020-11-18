# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountGroup(models.Model):
    _inherit = 'account.group'

    active = fields.Boolean(string='active', default=True)
