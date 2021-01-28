# -*- coding: utf-8 -*-
# Copyright (c) 2017 QubiQ (http://www.qubiq.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class MassReasignacionIniciativas(models.TransientModel):
    _name = 'mass.reasignacion.iniciativas'

    user_id = fields.Many2one(
        'res.users', string='Usuario', required=True)
    team_id = fields.Many2one(
        'crm.team', string='Equipo de ventas', required=True)
    company_id = fields.Many2one(
        'res.company', string='Compañía', required=True)

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            self.team_id = self.env['crm.team'].sudo().search([
                                    '|',
                                    ('member_ids', '=', self.user_id.id),
                                    ('user_id', '=', self.user_id.id)
                                ], limit=1).id or None
            self.company_id = self.user_id.company_ids[0].id or None
        return {'domain': {
                    'team_id': [
                        ('id', 'in',
                            self.env['crm.team'].sudo().search([
                                '|',
                                ('member_ids', '=', self.user_id.id),
                                ('user_id', '=', self.user_id.id)
                            ]).ids)],
                    'company_id': [('id', 'in', self.user_id.company_ids.ids)]
                    }}

    @api.multi
    def confirm(self):
        for sel in self:
            if sel.user_id and sel.team_id and sel.company_id:
                if sel.company_id.id != sel.team_id.company_id.id:
                    raise ValidationError(
                        'La compañia del equipo de venta y la seleccionada \
                        deben de ser la misma!')
                else:
                    for lead_obj in self.env['crm.lead'].sudo().search([
                            ('id', 'in', sel.env.context.get('active_ids', []))
                       ]):
                        vals = {
                            'company_id': sel.company_id.id,
                            'user_id': sel.user_id.id,
                            'team_id': sel.team_id.id,
                        }

                        for user in lead_obj.partner_id.user_ids:
                            print([user.name, user.company_ids,
                                   sel.company_id.id])
                            user.write({
                                'company_ids': [[4, sel.company_id.id, _]],
                                'company_id': sel.company_id.id
                            })

                        lead_obj.partner_id.write(vals)
                        lead_obj.write(vals)
            else:
                raise ValidationError(
                    'Se deben de seleccionar todos los campos!')
        return {'type': 'ir.actions.act_window_close'}
