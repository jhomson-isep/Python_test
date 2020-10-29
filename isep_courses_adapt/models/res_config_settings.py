from odoo import models, fields


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

    def auth_google_drive(self):
        model_path = os.path.dirname(os.path.abspath(__file__))
        credentials_file = model_path + "/drive/credentials.txt"
        drive_config_file = model_path + '/drive/client_secrets.json'
        GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = drive_config_file
        gauth.LoadCredentialsFile(credentials_file)
        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved credentials
            gauth.Authorize()
        # Save the current credentials to a file
        gauth.SaveCredentialsFile(credentials_file)
