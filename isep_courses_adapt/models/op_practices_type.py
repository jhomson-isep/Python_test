# -*- coding: utf-8 -*-

from odoo import models, fields


class OpPracticesType(models.Model):
    _name = "op.practices.type"
    _description = "Practices types"

    name = fields.Char('Name', size=128, required=True)
