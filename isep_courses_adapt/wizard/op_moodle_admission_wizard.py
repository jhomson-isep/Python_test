from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
from odoo.addons.isep_courses_adapt.models.moodle import MoodleLib
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)

class OpMoodleAdmissionWizard(models.TransientModel):
    _name = "op.moodle.admission.wizard"
    _description = "Moodle Admission Wizard"

    @api.onchange('category_id')
    def _get_domain(self):      
        return [('moodle_category', '=', str(self.category_id))]
    
    def _get_admission(self):
        admission_id = self.env.context.get('active_ids', []) or []
        admission = self.env['op.admission'].search([('id', '=', admission_id)])
        return admission
    
    category_id = fields.Many2one('op.moodle.category.rel',
                                  string="Select a Category")
    course_id = fields.Many2many('op.moodle.category.rel',
                                 domain=_get_domain,
                                 string="Select a Course")

    @api.multi
    def enroll_student(self):
        print("enroll")

    