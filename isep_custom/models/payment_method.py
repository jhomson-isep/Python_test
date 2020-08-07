# -*- coding: utf-8 -*-

from openerp import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class payment_method(models.Model):
    _inherit = 'payment.method'

    name = fields.Char(required=True)
    csv = fields.Char(string='CSV', size=4)
    acquirer_ref = fields.Char(size=16)
    caducidad = fields.Date(string='Fecha de caducidad', required=True)

    @api.model
    def default_get(self, fields):
        rec = super(payment_method, self).default_get(fields)
        acquirer_objs = self.env['payment.acquirer'].search([
                ('name', '=', 'Tarjeta de Credito'),
                ('company_id', '=', self.env.user.company_id.id)
                ])
        if len(acquirer_objs) == 1:
            rec['acquirer_id'] = acquirer_objs[0].id
        if 'partner_id' in rec:
            rec['name'] = self.env['res.partner'].browse(rec['partner_id'])[0].name
        return rec
