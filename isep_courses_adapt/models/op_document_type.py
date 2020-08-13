# -*- coding: utf-8 -*-

from odoo import models, fields


class OpDocumentType(models.Model):
    _name = "op.document.type"
    _description = "Student document type"

    name = fields.Char('Name', size=32, required=True)
