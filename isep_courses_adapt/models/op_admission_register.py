# -*- coding: utf-8 -*-

from odoo import fields, api, models


class OpAdmissionRegister(models.Model):
    _inherit = 'op.admission.register'

    batch_id = fields.Many2one('op.batch', string='Batch', required=True)

    @api.onchange('batch_id')
    def change_name(self):
        self.name = self.batch_id.name
