from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
from odoo.addons.isep_courses_adapt.models import moodle
import logging

logger = logging.getLogger(__name__)


class OpMoodleListCommissionWizard(models.TransientModel):
    _name = "op.moodle.list.commission.wizard"
    _description = "Comission List Moodle Wizard"

    moodle_commission_wizard = fields.Many2one('op.moodle.commission.wizard')
    group_change_wizard = fields.Many2one('op.student.group.change.wizard')
    moodle_course_id = fields.Integer(string="Course id")
    course_name = fields.Char(string="Course name")
    selected = fields.Boolean(string="Select", default=False)
    comission = fields.Char(string="Nombre Comision", required=True)
    comission_id = fields.Integer(string="Comission id")
    checked = fields.Boolean(string="Checked", default=False)
    moodle_course_line_ids = fields.One2many(
        'op.moodle.list.commission.wizard', 'moodle_commission_wizard',
        string='Course lines')

    @api.onchange('selected')
    def _onchange_selected(self):
        self.update({'selected': self.selected})

    def get_moodle_course_ids(self, commission_wizard_id):
        moodle_courses = self.search(
            [('moodle_commission_wizard', '=', commission_wizard_id),
             ('selected', '=', True)])
        return [moodle_course.moodle_course_id for moodle_course in moodle_courses]

    def get_moodle_course_by_group_change(self, change_wizard_id):
        moodle_courses = self.search(
            [('group_change_wizard', '=', change_wizard_id),
             ('selected', '=', True)])
        return [moodle_course.moodle_course_id for moodle_course in moodle_courses]


class OpMoodleCommissionWizard(models.TransientModel):
    _name = "op.moodle.commission.wizard"
    _description = "Moodle Commission Wizard"

    admission_id = fields.Many2one('op.admission', string="Admission")
    category_id = fields.Many2one('op.moodle.category.rel',
                                  string="Select a Category")
    moodle_course_line_ids_B = fields.One2many(
        'op.moodle.list.commission.wizard', 'moodle_commission_wizard',
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