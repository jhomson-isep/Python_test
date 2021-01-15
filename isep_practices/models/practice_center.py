from odoo import fields, models

class PracticeCenter(models.Model):
    _name = 'practice.center'
    _inherit = "mail.thread"
    _description = "Center"

    nif = fields.Char(string='NIF', size=20)
    name = fields.Char(string='Name', size=200)
    official_name = fields.Char(string='Official Name', size=200)
    coordinator = fields.Char(string='Coordinator', size=200)
    schedule = fields.Char(string='Schedule of Aplication', size=200)
    email = fields.Char('Email', size=128)
    web = fields.Char('Web', size=200)
    street = fields.Char('Street', size=200)
    city = fields.Char('City', size=200)
    code_postal = fields.Char('ZIP', size=10)
    province = fields.Char('Province', size=200)
    population = fields.Char('Population', size=200)
    observations = fields.Char('Observations', size=200)
    maximum_places = fields.Integer('Maximum Places')
    signatory = fields.Char('Signatory', size=200)
    signer_gender = fields.Selection([
        ('woman', 'Femenino'),
        ('man', 'Masculino'),
        ('other', 'Otros'),
    ], 'Gender Signer')
    practice_schedule_id = fields.Many2one('practice.schedule', string="Schedule")
    state_id = fields.Many2one('res.country.state', string="State", ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string="Country", ondelete='restrict')

    _sql_constraints = [
        ('unique_nif',
         'unique(nif)',
         'Nif must be unique per center!'),
        ('unique_email',
         'unique(email)',
         'Email must be unique per center!')
    ]