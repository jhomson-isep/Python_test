# -*- coding: utf-8 -*-
from odoo import models, fields, api


class OpAdmission(models.Model):
    _inherit = 'op.admission'

    observations = fields.Text(string='Observations')
    unsubscribed_date = fields.Date(string='Unsubscribed date')
    exam_on_campus = fields.Boolean(string='Exams in campus', default=False)
    temporary_leave = fields.Boolean(string='Temporary leave', default=False)
    academic_record_closing = fields.Date(string='Academic Record Closing '
                                                 'Date')
    mexico = fields.Boolean(string='Mexico', default=False)
    generation = fields.Integer(string='Generation')
    mx_documentation = fields.Char(string='MX Documentation')
    n_id = fields.Integer(string='External N_Id')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order Id')
    document_ids = fields.One2many("op.gdrive.documents", "partner_id",
                                   string="Documentation",
                                   related='partner_id.document_ids')
    # grade_ids = fields.One2many(comodel_name='op.exam.attendees',
    #                             inverse_name='op_student_course_id',
    #                             domain=[('is_final', '=', 'True')])
