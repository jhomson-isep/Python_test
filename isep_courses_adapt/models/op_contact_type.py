# -*- coding: utf-8 -*-

from odoo import models, fields


class OpContactType(models.Model):
    _name = "op.contact.type"
    _description = "Student contact type"

    name = fields.Char('Name', size=32, required=True)
