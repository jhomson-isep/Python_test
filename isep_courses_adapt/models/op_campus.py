# -*- coding: utf-8 -*-

from odoo import models, fields


class OpCampus(models.Model):
    _name = "op.campus"
    _description = "Campus"

    name = fields.Char('Name', size=128, required=True)
