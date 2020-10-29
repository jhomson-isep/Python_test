from odoo import models, fields


class OpFacultyGd(models.Model):
    _inherit = 'op.faculty'

    document_ids = fields.Many2one('op.document.type', string='Document Type')
