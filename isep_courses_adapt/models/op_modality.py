# -*- coding: utf-8 -*-

from odoo import models, fields


class OpModality(models.Model):
    _name = "op.modality"
    _description = "Modality"

    name = fields.Char('Name', size=128, required=True)
    code = fields.Char('Code', size=8, required=True)

    _sql_constraints = [
        ('unique_modality_code',
         'unique(code)', 'Code should be unique per modality!')]
