from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class PracticeTutor(models.Model):
    _name = 'practice.tutor'
    _inherit = "mail.thread"
    _inherits = {"res.partner": "partner_id"}
    _description = "Tutor"

    dni = fields.Char(string='Dni/Passport', size=30, required=True)
    partner_id = fields.Many2one('res.partner', 'Partner',
                                 required=True, ondelete="cascade")
    first_name = fields.Char('First Name', size=128, required=True)
    last_name = fields.Char('Last Name', size=128, required=True)
    emails = fields.Char('Email', size=128)


    _sql_constraints = [
        ('unique_dni',
         'unique(dni)',
         'Dni must be unique per tutor!'),
        ('unique_email',
         'unique(email)',
         'Email must be unique per tutor!'),
    ]

    @api.onchange('first_name', 'last_name')
    def _onchange_name(self):
        self.name = str(self.first_name) + \
                " " + str(self.last_name)

    @api.onchange('emails')
    def onchange_email(self):
        email_exist = self.env['res.partner'].search_count([('email', '=', self.emails), ('email', '!=', False)])
        if email_exist > 0:
            raise ValidationError(_(
                "Email exist in contact"))
        else:
            self.email = str(self.emails)

