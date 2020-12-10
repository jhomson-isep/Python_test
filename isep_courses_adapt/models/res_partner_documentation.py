# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartnerDocumentation(models.Model):
    _inherit = 'res.partner'

    document_ids = fields.One2many("op.gdrive.documents", "partner_id",
                                   string="Documentation")
