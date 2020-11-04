# -*- coding: utf-8 -*-

from odoo import models, fields


class OpDocumentType(models.Model):
    _name = "op.document.type"
    _description = "Student document type"

    name = fields.Char('Name', size=32, required=True)
    code = fields.Char('Code', size=12, required=True)

    _sql_constraints = [
        ('unique_document_type_code',
         'unique(code)', 'Code should be unique per document type!')]
