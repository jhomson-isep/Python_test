# -*- coding: utf-8 -*-

from odoo import models, fields


class OpWorkplace(models.Model):
    _name = "op.workplace"
    _description = "Workplace"

    name = fields.Char('Name', size=128, required=True)
    code = fields.Char('Code', size=8, required=True)

    _sql_constraints = [
        ('unique_workplace_code',
         'unique(code)', 'Code should be unique per workplace!')]
