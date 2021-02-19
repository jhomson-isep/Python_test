# -*- encoding: utf-8 -*-
from odoo import fields, models, api

class PracticeCenterTutor(models.Model):
    _name = 'practice.center.tutor'
    _description = "Association tutor with center"
    _rec_name = 'tutor_id'

    tutor_id = fields.Many2one('res.partner', string="Tutor", required=True)
    partner_id = fields.Many2one('res.partner')

    @api.onchange('tutor_id')
    def filterPartnerByTutor(self):
        return {'domain': {'tutor_id': [('tutor', '=', True)]}}
