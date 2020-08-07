# -*- coding: utf-8 -*-

from openerp import api, fields, models


class mail_message(models.Model):
    _inherit = 'mail.message'

    x_leadid = fields.Many2one('crm.lead', string="Iniciativa/Oportunidad Asociada")
    x_body_html = fields.Text(string="Asunto/Contenidos")
    x_duracionsegundos = fields.Integer(string="Duracion en Segundos")
    x_duraciontexto = fields.Char(string="Duracion")
    x_extension = fields.Integer(string="Extension")
