from odoo import fields, models

class PracticePractice(models.Model):
    _name = 'practice.practice'
    _inherit = "mail.thread"
    _description = "Practice"

    weekly_hours = fields.Integer(string='Weekly Hours')
    total_hours = fields.Integer(string='Total Hours')
    start_date = fields.Date(string='Start Date')
    final_date = fields.Date(string='Start Date')
    practice_temary_id = fields.Many2one('practice.temary', string='Temary')
    practice_tutor_id = fields.Many2one('practice.tutor', string='Tutor')
    practice_center_id = fields.Many2one('practice.center', string='Center')
    practice_phase_id = fields.Many2one('practice.phase', string='Phase')
    op_course_id = fields.Many2one('op.course', string='Course')
    op_student_id = fields.Many2one('op.student', string='Student')
    signed_agreement = fields.Boolean(string='Signed Agreement')
    assistance_received = fields.Boolean(string='Assistance Received')
    evaluation_received = fields.Boolean(string='Evaluation Received')
    invoice_received = fields.Boolean(string='Invoice Received')
    remuneration_center = fields.Float(string='Remuneration Center')
    expected_end_date = fields.Date(string='Expected End Date')
