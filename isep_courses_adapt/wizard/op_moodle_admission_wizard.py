from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
from odoo.addons.isep_courses_adapt.models import moodle
import logging

logger = logging.getLogger(__name__)


class OpMoodleAdmissionWizard(models.TransientModel):
    _name = "op.moodle.admission.wizard"
    _description = "Moodle Admission Wizard"
    
    def _get_admission(self):
        admission_id = self.env.context.get('active_ids', []) or []
        admission = self.env['op.admission'].search([('id', '=', admission_id)])
        return admission
    
    category_id = fields.Many2many('op.moodle.category.rel',
                                  string="Select a Category")

    @api.multi
    def enroll_student(self):
        if self.category_id is None:
            raise  ValidationError(_('Debe de seleccionar un categoria!!!'))
        admission = self._get_admission()
        admission.enroll_student(self.category_id)
