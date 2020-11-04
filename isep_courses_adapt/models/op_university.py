# -*- coding: utf-8 -*-

from odoo import models, fields


class OpUniversity(models.Model):
    _name = "op.university"
    _description = "Openeducat university"

    name = fields.Char('Name', size=128, required=True)
    code = fields.Char('Code', size=32, required=True)
