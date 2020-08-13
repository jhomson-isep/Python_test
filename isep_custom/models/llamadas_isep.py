# -*- coding: utf-8 -*-
import logging
from openerp import api, fields, models, _
_logger = logging.getLogger(__name__)


class llamadas_isep(models.Model):
    _name = 'llamadas.isep'
    _description = "Llamadas Centralita"
    name = fields.Char(string='Nombre', help="Nombre de este registro")
    extension = fields.Char(string='Extension')
    telefono = fields.Char(string='Telefono')
    date_ini = fields.Datetime(string='Inicio')
    date_out = fields.Datetime(string='Fin')
    note = fields.Text(string='Notas')
    duracion = fields.Float(string='Duración')
    #user_id = fields.Many2one('res.users', string="Usuario")
    employee = fields.Many2one('hr.employee', string="Empleado")
    opportunity_id = fields.Many2one('crm.lead', string="Iniciativa")
    entidad = fields.Char(string="Entidad")
    empleado = fields.Many2one('hr.employee', string="Empleado")
    recuento_llamadas = fields.Integer(
        compute='_count_calls',
        string="Número de llamadas",
        readonly=True)
    notas = fields.Text(string="Detalles llamada")
    efectiva = fields.Boolean(string="Contacto efectivo")
    check_employee = fields.Boolean(string="Empleado", default=False)
    llamadas_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente")

    @api.multi
    def _count_calls(self):
        nbr_obj = self.env['llamadas.isep']
        for s in self:
            s.recuento_llamadas = nbr_obj.search_count(
                [('telefono', '=', self.telefono)])