# -*- coding: utf-8 -*-

from odoo import models, fields


class OpStudyType(models.Model):
    _name = "op.study.type"
    _description = "study type"

    name = fields.Char('Name', size=32, required=True)
