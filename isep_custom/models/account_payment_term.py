# -*- coding: utf-8 -*-

from openerp import api, fields, models


class account_payment_term(models.Model):
    _inherit = 'account.payment.term'

    x_Penalizacion_Porcentaje = fields.Float(string="% Penalización")
    x_Penalizacion = fields.Float(string="Penalización")
    x_Alias = fields.Char(string="Alias")
    x_company_ids = fields.Many2many('res.company',string="Compañías permitidas")