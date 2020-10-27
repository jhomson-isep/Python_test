from odoo import models, fields
from pydrive.auth import GoogleAuth
import base64


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    moodle_token = fields.Char(string="Moodle token",
                               config_parameter='moodle_token', size=128)
    moodle_url = fields.Char(string="Moodle URL",
                             config_parameter='moodle_url', size=128)
    moodle_endpoint = fields.Char(string="Moodle endpoint",
                                  config_parameter='moodle_endpoint',
                                  default="/webservice/rest/server.php")
    send_moodle = fields.Boolean(string='Send moodle', default=False)
    courses_limit = fields.Integer(string="Courses limit", default=100,
                                   config_parameter='courses_limit')
    client_id = fields.Char(string='Client Id Google',
                            config_parameter='client_id', size=128)
    client_secret = fields.Char(string="Client Secret Code Google",
                                config_parameter='client_secret', size=128)
    save_credentials = fields.Boolean(string='Save Credentials', default=True,
                                        config_parameter='save_credentials')
    save_credentials_backend = fields.Char(string='Type of Credentials settings', default='file',
                                            config_parameter='save_credentials_backend')
    save_credentials_file = fields.Char(string='Name of file Credentials', default='credentials.json',
                                        config_parameter='save_credentials_file')
    get_refresh_token = fields.Boolean(string='Refresh Token', default=True,
                                        config_parameter='get_refresh_token')

    def create_file(self):
        config_params = self.env['ir.config_parameter'].sudo()
        client_id = config_params.get_param('client_id')
        client_secret = config_params.get_param('client_secret')
        save_credentials = config_params.get_param('save_credentials')
        save_credentials_backend = config_params.get_param('save_credentials_backend')
        save_credentials_file = config_params.get_param('save_credentials_file')
        get_refresh_token = config_params.get_param('get_refresh_token')

        with open('settings.yaml', 'w+') as file:
            content = '''client_config_backend: %s
client_config:
  client_id: %s
  client_secret: %s

save_credentials: %s
save_credentials_backend: %s
save_credentials_file: %s

get_refresh_token: %s
'''.format(client_id, client_secret, save_credentials, save_credentials_backend, save_credentials_file, get_refresh_token)
            file.write(content)
            file.close()
        self.get_access()

    def get_access(self):
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()