from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
from odoo.addons.isep_courses_adapt.models import moodle
import logging

logger = logging.getLogger(__name__)


class OpMoodleAdmissionWizard(models.TransientModel):
    _name = "op.moodle.admission.wizard"
    _description = "Moodle Admission Wizard"

    @api.model
    def _get_categorys(self):
        choices = list()
        Moodle = moodle.MoodleLib()
        response = Moodle.get_course_by_field(field="category", value="113")
        # 287 Athhome
        courses = response['courses']
        courses.sort(key=self.get_order)
        for course in courses:
            choices.append((course.get('id'), course.get('fullname')))
        return choices

    @api.onchange('category_id')
    def _get_domain(self):
        return [('moodle_category', '=', str(self.category_id))]

    category_id = fields.Selection(selection=_get_categorys,
                                   string="Select a course")
    course_id = fields.Many2many('op.moodle.category.rel',
                                 domain=_get_domain)

    def get_order(self, course):
        return course.get('sortorder')

    def enroll(self):
        print('enroll')
