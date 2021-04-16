from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
#from odoo.addons.isep_courses_adapt.models import moodle
import logging

logger = logging.getLogger(__name__)

#Se define el modelo (clase) para el Wizard.
#TransientModel indica que se trata de un modelo (clase models) en el cual sus datos permaneceran
#durante un tiempo en el sistema Odoo, luego se eliminaran automaticamente.

class OpAdmisionesPedidosDeVentaWizard(models.TransientModel):
    #Se define el nombre y descripcion del modulo en el sistema Odoo
    _name = "op.admisiones.pedidos.de.venta.wizard"
    _description = "Wizard de Admisiones y pedidos de ventas"

    #Se definen los campos (fields) que indican lo que el modelo puede guardar y donde.
    fecha = fields.Char(string="Fecha", required=True)
    compania = fields.Char(string="Compañia", required=True)
    status_adm = fields.Char(string="Status de Admisión", required=True)
    selected = fields.Boolean(string="Select", default=False)

    #Se definen funciones relacionadas
    @api.onchange('selected')
    def _onchange_selected(self):
        self.update({'selected': self.selected})