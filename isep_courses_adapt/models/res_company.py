# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    principal_id = fields.Many2one('res.partner', 'Principal')
    academic_director_id = fields.Many2one('res.partner', 'Academic director')
