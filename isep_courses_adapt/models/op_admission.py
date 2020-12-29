# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from .moodle import MoodleLib
from datetime import date
import logging
import string
import random

logger = logging.getLogger(__name__)
LETTERS = string.ascii_letters
NUMBERS = string.digits
PUNCTUATION = '@@$#'


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
    mx_documentation = fields.Boolean(string='MX Documentation', default=False)
    n_id = fields.Integer(string='External N_Id')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order Id')
    document_ids = fields.One2many("op.gdrive.documents", "partner_id",
                                   string="Documentation",
                                   related='partner_id.document_ids')
    application_number = fields.Char(
        'Application Number', size=32, copy=False,
        required=True, readonly=True, store=True,
        default=lambda self:
        self.env['ir.sequence'].next_by_code('op.admission'))
    phone = fields.Char(
        'Phone', size=32, states={'done': [('readonly', True)],
                                  'submit': [('required', True)]})
    mobile = fields.Char(
        'Mobile', size=32,
        states={'done': [('readonly', True)], 'submit': [('required', True)]})

    # grade_ids = fields.One2many(comodel_name='op.exam.attendees',
    #                             inverse_name='admission_id',
    #                             domain=[('is_final', '=', 'True')])

    @api.multi
    def enroll_student(self):
        super(OpAdmission, self).enroll_student()
        for record in self:
            record.create_moodle_user()

    @api.one
    def create_moodle_user(self):
        Moodle = MoodleLib()
        student = self.env['op.student'].search(
            [('id', '=', self.student_id.id)], limit=1)
        student_course = self.env['op.student.course'].search(
            [('student_id', '=', student.id),
             ('batch_id', '=', self.batch_id.id)])
        print("Student id: ", student.id)
        moodle_course = Moodle.get_course(self.batch_id.moodle_code)
        print("moodle_course: ", moodle_course)
        moodle_group = Moodle.get_group(moodle_course.get('id'),
                                        self.batch_id.code)
        if moodle_group is None:
            moodle_group = Moodle.core_group_create_groups(
                self.batch_id.code, moodle_course.get('id'))
        print("moodle_group: ", moodle_group)
        password = self.password_generator(length=10)
        user = Moodle.get_user_by_field(field="username",
                                        value=self.partner_id.email)
        if user is None:
            user_response = Moodle.create_users(
                firstname=self.first_name,
                lastname=self.last_name,
                dni=self.partner_id.num_reg_trib or self.partner_id.vat,
                password=password,
                email=self.partner_id.email)
            user = user_response[0]
        print("user: ", user)
        enrol_result = Moodle.enrol_user(moodle_course.get('id'),
                                         user.get('id'))
        logger.info(enrol_result)
        member_result = Moodle.add_group_members(moodle_group.get('id'),
                                                 user.get('id'))
        logger.info(member_result)
        gr_no = self.env['ir.sequence'].next_by_code('op.gr.number') or '0'
        student_course.write({'roll_number': gr_no})
        student.write({
            'moodle_id': user.get('id'),
            'moodle_user': self.partner_id.email,
            'moodle_pass': password,
            'gr_no': gr_no,
            'n_id': gr_no
        })

    @staticmethod
    def password_generator(length=8):
        """
        Generates a random password having the specified length
        :length -> length of password to be generated. Defaults to 8
            if nothing is specified.
        :returns string <class 'str'>
        """
        # create alphanumerical from string constants
        printable = f'{LETTERS}{NUMBERS}{PUNCTUATION}'

        # convert printable from string to list and shuffle
        printable = list(printable)
        random.shuffle(printable)

        # generate random password and convert to string
        random_password = random.choices(printable, k=length)
        random_password = ''.join(random_password)
        return random_password

    @api.model
    def date_finish(self):
        op_batch = self.env['op.batch'].search([])
        op_student = self.env['op.student'].search([])
        for batch in op_batch:
            for student in op_student:
                op_admission = self.search([('student_id', '=', student.id),
                                            ('active', '=', True)])
                op_exam_attendees = self.env['op.exam.attendees'].search(
                    [('student_id', '=', student.id),
                     ('batch_id', '=', batch.id)])
                subjects_presented = 0
                total_subject = self.env['op.batch.subject.rel'].search_count(
                    [('batch_id', '=', batch.id)])
                if len(op_exam_attendees) > 0:
                    logger.info(op_exam_attendees)
                    for exam_attendees in op_exam_attendees:
                        if exam_attendees.marks > 0:
                            subjects_presented += 1
                    if total_subject == subjects_presented:
                        if not op_admission.academic_record_closing:
                            values = {
                                'academic_record_closing': date.today()
                            }
                            op_admission.write(values)
                            logger.info('****************************************')
                            logger.info('*    UPDATE DATE OF ACADEMIC CLOSING   *')
                            logger.info('****************************************')
