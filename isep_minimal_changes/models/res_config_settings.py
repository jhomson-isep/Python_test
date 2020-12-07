# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sign_outgoing_mail_server = fields.Boolean(
        string="Specific Mail Server",
        config_parameter='sign.outgoing_mail_server',
        help='Use a specific mail server in priority. Otherwise Odoo relies '
             'on the first outgoing mail server available (based on their '
             'sequencing) as it does for normal mails.')
    sign_mail_server_id = fields.Many2one(
        'ir.mail_server',
        string='Mail Server',
        config_parameter='sign_mail_server_id')

    @api.onchange('sign_outgoing_mail_server')
    def _onchange_mass_mailing_outgoing_mail_server(self):
        if not self.sign_outgoing_mail_server:
            self.sign_mail_server_id = False
