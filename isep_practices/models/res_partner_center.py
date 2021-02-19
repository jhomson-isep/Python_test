# -*- encoding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ResPartnerCenter(models.Model):
    _name = "res.partner"
    _inherit = "res.partner"

    #fields of center
    center = fields.Boolean(string='Is Center', default=False)
    name_official = fields.Char(string="Name Official")
    coordinator = fields.Char(string="Coordinator")
    maximum_places = fields.Integer(string="Maximum Places")
    signatory = fields.Char(string="Signatory")
    practice_schedule_id = fields.Many2one('practice.schedule', string="Schedule")
    #field of tutor
    tutor = fields.Boolean(string='Is Tutor', default=False)
    email = fields.Char(required=True)
    tutor_course_ids = fields.One2many('practice.tutor.course', 'partner_id', string='Course')
    center_course_ids = fields.One2many('practice.center.course', 'partner_id', string='Course')
    center_tutor_ids = fields.One2many('practice.center.tutor', 'partner_id', string='Tutor')



    @api.onchange('email')
    def _change_email(self):
        if self.email:
            partner = self.search([('email', '=', self.email)])
            if self.email:
                if len(partner) > 0:
                    print("NO VALIDO")
                    self.email = not self.email
                    raise ValidationError(
                        _("The Email cannot be set equal."))

    def search_error(self):
        return str(self.email).find("@gmail.com")

    @api.onchange('email')
    def _validar_email(self):
        if self.email:
            print(self.search_error())
            if self.search_error() == -1:
                raise ValidationError(
                    _("Email no valido"))


