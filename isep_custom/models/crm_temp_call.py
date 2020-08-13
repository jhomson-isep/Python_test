# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class crm_temp_call(models.Model):
    _name = 'crm.temp.call'

    name = fields.Char()
    inicio = fields.Datetime(string="Inicio de la llamada")
    fin = fields.Datetime(string="Fin de la llamada")
    user = fields.Char(string="Usuario")
    duracion = fields.Float(string="Duración de la llamada")
    caller = fields.Char(string="caller")
    extension = fields.Char(string="Extensión")
    llamado = fields.Char(string="Número marcado")
    entidad = fields.Char(string="Entidad")
    other = fields.Text(string="Url")
    check = fields.Boolean(string="Pasado")

    @api.multi
    def calls_cron(self):
        temp_call_obj = self.env['crm.temp.call'].search(
            [('check', '=', False)])

        for call in temp_call_obj:
            opor_id = ''
            partner_id = ''
            employee_id = ''
            check_employee = False

            if len(call.llamado) > 4:
                client_obj = self.env['crm.lead'].search(
                    [('phone', '=', call.llamado)])

                if len(client_obj) < 1:
                    client_obj = self.env['crm.lead'].search(
                        [('mobile', '=', call.llamado)])

                if len(client_obj) > 1:
                    partner_id = client_obj[0].partner_id.id
                else:
                    partner_id = client_obj.partner_id.id

                if str(client_obj.type) == "opportunity":
                    opor_id = client_obj.id

            else:
                employee_obj = self.env['hr.employee'].search(
                    [('work_phone', '=', call.llamado)])
                employee_id = employee_obj[0].id

            empleado = self.env['hr.employee'].search(
                [('work_phone', '=', self.extension)])

            if len(empleado) > 1:
                empleado = empleado[0].id
            else:
                empleado = empleado.id

            if call.duracion > 0.16:
                val = True
            else:
                val = False

            vals = {
                'date_ini': call.inicio,
                'date_out': call.fin,
                'extension': call.extension,
                'telefono': call.llamado,
                'name': partner_id or '',
                'employee': employee_id or '',
                'opportunity_id': opor_id or '',
                'entidad': call.entidad,
                'duracion': call.duracion,
                'empleado': empleado or '',
                'efectiva': val,
                'check_employee': check_employee
                }

            call_obj = self.env['llamadas.isep']
            call_obj.sudo().create(vals)
            call.check = True

    @api.one
    def validate_call(self):
        for s in self:
            opor_id = ''
            partner_id = None
            employee_id = ''
            check_employee = False

            if len(s.llamado) > 4:
                client_obj = self.env['crm.lead'].search(
                    [('phone', '=', s.llamado)])
                
                if len(client_obj) < 1:
                    client_obj = self.env['crm.lead'].search(
                        [('mobile', '=', s.llamado)])

                if len(client_obj) > 1:
                    partner_id = client_obj[0].partner_id.id
                else:
                    partner_id = client_obj.partner_id.id

                if str(client_obj.type) == "opportunity":
                    opor_id = client_obj.id

            else:
                employee_obj = self.env['hr.employee'].search(
                    [('work_phone', '=', s.llamado)])
                employee_id = employee_obj[0].id

                check_employee = True

            empleado = self.env['hr.employee'].search(
                [('work_phone', '=', self.extension)])

            if len(empleado) > 1:
                empleado = empleado[0].id
            else:
                empleado = empleado.id

            if s.duracion > 0.16:
                val = True
            else:
                val = False

            vals = {
                'date_ini': s.inicio,
                'date_out': s.fin,
                'extension': s.extension,
                'telefono': s.llamado,
                'name': s.name,
                'llamadas_id': partner_id or None,
                'employee': employee_id or '',
                'opportunity_id': opor_id or '',
                'entidad': s.entidad,
                'duracion': s.duracion,
                'empleado': empleado or '',
                'efectiva': val,
                'check_employee': check_employee
                }

            call_obj = self.env['llamadas.isep']
            call_obj.sudo().create(vals)
            s.check = True