from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
from odoo.addons.isep_courses_adapt.models import moodle
import logging

logger = logging.getLogger(__name__)


class OpMoodleCoursesWizard(models.TransientModel):
    _name = "op.moodle.courses.wizard"
    _description = "Moodle Courses Wizard"

    moodle_admission_wizard = fields.Many2one('op.moodle.admission.wizard')
    moodle_course_id = fields.Integer(string="Course id")
    course_name = fields.Char(string="Course name")
    selected = fields.Boolean(string="Select", default=False)

    @api.onchange('selected')
    def _onchange_selected(self):
        self.update({'selected': self.selected})

    def get_moodle_course_ids(self, admission_wizard_id):
        moodle_courses = self.search(
            [('moodle_admission_wizard', '=', admission_wizard_id),
             ('selected', '=', True)])
        return [moodle_course.moodle_course_id for moodle_course in moodle_courses]


class OpMoodleAdmissionWizard(models.TransientModel):
    _name = "op.moodle.admission.wizard"
    _description = "Moodle Admission Wizard"

    admission_id = fields.Many2one('op.admission', string="Admission")
    category_id = fields.Many2one('op.moodle.category.rel',
                                  string="Select a Category")
    moodle_course_line_ids = fields.One2many(
        'op.moodle.courses.wizard', 'moodle_admission_wizard',
        string='Course lines')

    def _get_admission(self):
        admission_id = self.env.context.get('active_ids', []) or []
        return self.env['op.admission'].search([('id', 'in', admission_id)])

    @api.multi
    def enroll_student(self):
        moodle_course_ids = self.env[
            'op.moodle.courses.wizard'].get_moodle_course_ids(self.id)
        if len(moodle_course_ids) == 0:
            raise ValidationError(_('Debe de seleccionar al menos un '
                                    'módulo para matricular!!!'))
        logger.info(moodle_course_ids)
        self.admission_id.enroll_student(moodle_course_ids)
