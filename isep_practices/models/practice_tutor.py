from odoo import fields, models, api

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

    _sql_constraints = [
        ('unique_dni',
         'unique(dni)',
         'Dni must be unique per tutor!')
    ]

    @api.onchange('first_name', 'last_name')
    def _onchange_name(self):
        self.name = str(self.first_name) + \
                " " + str(self.last_name)
