from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    moodle_token = fields.Char(string="Moodle token", config_parameter='moodle_token', size=128)
    moodle_url = fields.Char(string="Moodle URL", config_parameter='moodle_url', size=128)
    moodle_endpoint = fields.Char(string="Moodle endpoint", config_parameter='moodle_endpoint',
                                  default="/webservice/rest/server.php")
