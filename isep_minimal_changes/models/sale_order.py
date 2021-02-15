# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    active = fields.Boolean(string='active', default=True)
    typeform_partner_url = fields.Char(string="typeform_partner_url",
                                       compute='_compute_typeform_partner_url')

    @api.multi
    def _compute_typeform_partner_url(self):
        for order in self:
            if order.partner_id:
                url_name = order.partner_id.name.replace(' ', '+')
                order.typeform_partner_url = "https://universidadisep.typeform.com/to/qEZyoSJu#idpartner={0}&partner={1}".format(
                    order.partner_id.id, url_name)

    @api.one
    def action_credit_card_typeform(self):
        mail_template = self.env.ref(
            'isep_minimal_changes.mail_credit_card_typeform')
        mail_template.send_mail(self.id, force_send=True)
