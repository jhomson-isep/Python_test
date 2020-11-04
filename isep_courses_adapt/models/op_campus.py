# -*- coding: utf-8 -*-

from odoo import models, fields


class OpCampus(models.Model):
    _name = "op.campus"
    _description = "Campus"

    name = fields.Char('Name', size=128, required=True)
    code = fields.Char('Code', size=8, required=True)

    _sql_constraints = [
        ('unique_campus_code',
         'unique(code)', 'Code should be unique per campus!')]
