# -*- encoding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class PracticePractice(models.Model):
    _name = 'practice.practice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Practice"

    weekly_hours = fields.Float(string='Weekly Hours', compute="_compute_weekly_hours", store=True)
    total_hours = fields.Float(string='Total Hours', compute="_compute_total_hours", store=True)
    start_date = fields.Datetime(string='Start Date')
    final_date = fields.Datetime(string='Final Date')
    #practice_temary_id = fields.Many2one('practice.temary', string='Temary')
    tutor_id = fields.Many2one('res.partner', string='Tutor')
    op_student_id = fields.Many2one('op.student', string='Student')
    op_admission_id = fields.Many2one("op.admission", 'Admission')
    status_phase = fields.Selection([
        ('requested', 'Solicitada'),
        ('assigned', 'Asignada'),
        ('started', 'Iniciada'),
        ('finished', 'Finalizada'),
        ('not finished', 'No Finalizada'), ], 'Phase', track_visibility='onchange', default="started")
    op_course_id = fields.Many2one('op.course', string='Course', related='op_admission_id.course_id', store=True)
    remuneration_center = fields.Float(string='Remuneration Center')
    center_id = fields.Many2one('res.partner', string='Center')
    payment_center = fields.Boolean(string='Payment to the Center', default=False)

    '''
    def _check_dates(self, cr, uid, ids, context=None):
        print('Paso')
        for rec in self.browse(cr, uid, ids):
            start_date = rec.start_date
            final_date = rec.final_date
            if start_date < final_date:
                return True
        return False
    '''
    _sql_constraints = [
        ('check_dates',
         'CHECK (start_date <= final_date)',
         'Fecha de inicio no debe ser menor a fecha final.'),
    ]

    @api.onchange('center_id')
    def filterContactByCenter(self):
        return {'domain': {'center_id': [('center', '=', True)]}}

    @api.onchange('tutor_id')
    def filterContactByTutor(self):
        return {'domain': {'tutor_id': [('tutor', '=', True)]}}

    @api.onchange('op_admission_id', 'op_student_id')
    def filterAdmisionByStudent(self):
        return {'domain': {'op_admission_id': [('student_id', '=', self.op_student_id.id)]}}

    def getDay(self):
        if self.start_date and self.final_date:
            start_date_new = datetime.strptime(str(self.start_date), "%Y-%m-%d %H:%M:%S").date()
            final_date_new = datetime.strptime(str(self.final_date), "%Y-%m-%d %H:%M:%S").date()
            result_date = final_date_new-start_date_new
            days = str(result_date).replace(' days, 0:00:00', '')
            weeks = int(days)//7
            return weeks

    @api.one
    @api.depends('start_date','final_date','total_hours')
    def _compute_weekly_hours(self):
        if self.total_hours > 0 and self.start_date and self.final_date:
            self.weekly_hours = self.total_hours / self.getDay()

    @api.one
    @api.depends('op_admission_id')
    def _compute_total_hours(self):
        print(self.op_admission_id.batch_id.code)
        op_batch = self.env['op.batch'].search([('code', '=', self.op_admission_id.batch_id.code)])
        print(op_batch)
        op_batch_subject_rel = op_batch.op_batch_subject_rel_ids
        for op_batch_subject in op_batch_subject_rel:
            if 'práctica' in str(op_batch_subject.subject_id.name).lower():
                print(op_batch_subject.hours)
                self.total_hours = op_batch_subject.hours
                break