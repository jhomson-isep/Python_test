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
    due_date = fields.Date(string='Due Date')
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

    @api.multi
    def enroll_student(self):
        super(OpAdmission, self).enroll_student()
        for record in self:
            record.create_moodle_user()

    @api.multi
    def submit_form(self):
        for admission in self:
            admission.state = 'admission'

    @api.one
    def create_moodle_user(self):
        moodle = MoodleLib()
        student = self.env['op.student'].search(
            [('id', '=', self.student_id.id)], limit=1)
        student_course = self.env['op.student.course'].search(
            [('student_id', '=', student.id),
             ('batch_id', '=', self.batch_id.id)])
        print("Student id: ", student.id)
        logger.info("Student id: {}".format(student.id))
        moodle_course = moodle.get_course(self.batch_id.moodle_code)
        print("moodle_course: ", moodle_course)
        logger.info("moodle_course: {}".format(moodle_course))
        moodle_group = moodle.get_group(moodle_course.get('id'),
                                        self.batch_id.code)
        if moodle_group is None:
            moodle_group = moodle.core_group_create_groups(
                self.batch_id.code, moodle_course.get('id'))
        print("moodle_group: ", moodle_group)
        logger.info("moodle_group: {}".format(moodle_group))
        password = self.password_generator(length=10)
        user = moodle.get_user_by_field(field="username",
                                        value=self.partner_id.email)
        if user is None:
            user_response = moodle.create_users(
                firstname=self.first_name,
                lastname=self.last_name,
                dni=self.partner_id.vat,
                password=password,
                email=self.partner_id.email)
            user = user_response[0]
        print("user: ", user)
        logger.info("user: {}".format(user))
        enrol_result = moodle.enrol_user(moodle_course.get('id'),
                                         user.get('id'))
        logger.info(enrol_result)
        member_result = moodle.add_group_members(moodle_group.get('id'),
                                                 user.get('id'))
        logger.info(member_result)
        gr_no = self.env['ir.sequence'].next_by_code('op.gr.number') or '0'
        logger.info(gr_no)
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
        op_batch = self.env['op.batch'].search([('end_date', '>=', date.today())])
        for batch in op_batch:
            op_student_course = batch.student_lines
            logger.info(op_student_course)
            for student_course in op_student_course:
                op_admission = self.search([('student_id', '=', student_course.student_id.id), ('academic_record_closing', '=', False)])
                logger.info(op_admission)
                subjects_presented = self.env['op.exam.attendees'].search_count(
                    [('student_id', '=', student_course.student_id.id),
                     ('batch_id', '=', batch.id), ('marks', '>', 0)])
                total_subject = self.env['op.batch.subject.rel'].search_count(
                    [('batch_id', '=', batch.id)])
                if total_subject > 0 and len(op_admission) > 0:
                    if total_subject == subjects_presented:
                        values = {
                                'academic_record_closing': date.today()
                        }
                        op_admission.write(values)
                        logger.info('****************************************')
                        logger.info('*    UPDATE DATE OF ACADEMIC CLOSING   *')
                        logger.info('****************************************')

    @api.multi
    def get_student_vals(self):
        for student in self:
            student_user = self.env['res.users'].search(
                [('login', '=', student.email)], limit=1)
            if len(student_user) == 0:
                student_user = self.env['res.users'].create({
                    'name': student.name,
                    'login': student.email,
                    'image': self.image or False,
                    'is_student': True,
                    'groups_id': [
                        (6, 0,
                         [self.env.ref('base.group_portal').id])]
                })
            details = {
                'phone': student.phone,
                'mobile': student.mobile,
                'email': student.email,
                'street': student.street,
                'street2': student.street2,
                'city': student.city,
                'country_id':
                    student.country_id and student.country_id.id or False,
                'state_id': student.state_id and student.state_id.id or False,
                'image': student.image,
                'zip': student.zip,
            }
            student_user.partner_id.write(details)
            details.update({
                'title': student.title and student.title.id or False,
                'first_name': student.first_name,
                'middle_name': student.middle_name,
                'last_name': student.last_name,
                'birth_date': student.birth_date,
                'gender': student.gender,
                'course_id':
                    student.course_id and student.course_id.id or False,
                'batch_id':
                    student.batch_id and student.batch_id.id or False,
                'image': student.image or False,
                'course_detail_ids': [[0, False, {
                    'date': fields.Date.today(),
                    'course_id':
                        student.course_id and student.course_id.id or False,
                    'batch_id':
                        student.batch_id and student.batch_id.id or False,
                }]],
                'user_id': student_user.id,
                'partner_id': student_user.partner_id.id,
            })
            return details
