# -*- coding: utf-8 -*-
import logging
from openerp import api, fields, models, _
_logger = logging.getLogger(__name__)


class hrEmployee(models.Model):
    _inherit = "hr.employee"

    nombre_empleado = fields.One2many(
        comodel_name="llamadas.isep",
        inverse_name="employee")