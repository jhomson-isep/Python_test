# -*- coding: utf-8 -*-

from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
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
    due_date = fields.Date('Due Date', states={'done': [('readonly', False)]})
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
        for record in self:
            if record.register_id.max_count:
                total_admission = self.env['op.admission'].search_count(
                    [('register_id', '=', record.register_id.id),
                     ('state', '=', 'done')])
                if not total_admission < record.register_id.max_count:
                    msg = 'Max Admission In Admission Register :- (%s)' % (
                        record.register_id.max_count)
                    raise ValidationError(_(msg))

            student = self.env['op.student'].search(
                [('email', '=', record.email)], limit=1)
            if len(student) > 0:
                record.student_id = student.id

            print(len(student))
            print(record.student_id)

            if not record.student_id:
                vals = record.get_student_vals()
                record.partner_id = vals.get('partner_id')
                record.student_id = student_id = self.env[
                    'op.student'].create(vals).id
            else:
                student_id = record.student_id.id
                record.student_id.write({
                    'course_detail_ids': [[0, False, {
                        'course_id':
                            record.course_id and record.course_id.id or False,
                        'batch_id':
                            record.batch_id and record.batch_id.id or False,
                    }]],
                })
            if record.fees_term_id:
                val = []
                product_id = record.register_id.product_id.id
                for line in record.fees_term_id.line_ids:
                    no_days = line.due_days
                    per_amount = line.value
                    amount = (per_amount * record.fees) / 100
                    date = (datetime.today() + relativedelta(
                        days=no_days)).date()
                    dict_val = {
                        'fees_line_id': line.id,
                        'amount': amount,
                        'fees_factor': per_amount,
                        'date': date,
                        'product_id': product_id,
                        'state': 'draft',
                    }
                    val.append([0, False, dict_val])
                record.student_id.write({
                    'fees_detail_ids': val
                })
            record.write({
                'nbr': 1,
                'state': 'done',
                'admission_date': fields.Date.today(),
                'student_id': student_id,
                'is_student': True,
            })
            reg_id = self.env['op.subject.registration'].create({
                'student_id': student_id,
                'batch_id': record.batch_id.id,
                'course_id': record.course_id.id,
                'min_unit_load': record.course_id.min_unit_load or 0.0,
                'max_unit_load': record.course_id.max_unit_load or 0.0,
                'state': 'draft',
            })
            reg_id.get_subjects()
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
        logger.info("Student id: {}".format(student.id))
        moodle_course = moodle.get_course(self.batch_id.moodle_code)
        modality = list()
        moodle_cohort = None
        logger.info("moodle_course: {}".format(moodle_course))
        moodle_group = moodle.get_group(moodle_course.get('id'),
                                        self.batch_id.code)
        if moodle_group is None:
            moodle_group = moodle.core_group_create_groups(
                self.batch_id.code, moodle_course.get('id'))
        logger.info("moodle_group: {}".format(moodle_group))
        password = self.password_generator(length=10)
        user = moodle.get_user_by_field(field="email",
                                        value=self.partner_id.email.lower())
        if student.gr_no:
            gr_no = student.gr_no
        else:
            gr_no = self.env['ir.sequence'].next_by_code('op.gr.number') or '0'

        student_values = {}
        if user is None:
            first_name = self.first_name
            if self.middle_name:
                first_name = ' '.join([first_name, self.middle_name])

            user_response = moodle.create_users(
                firstname=first_name,
                lastname=self.last_name,
                dni=self.partner_id.vat,
                password=password,
                email=self.partner_id.email.lower())
            user = user_response[0]
            logger.info(gr_no)
            student_values = {
                'moodle_id': user.get('id'),
                'moodle_user': self.partner_id.email,
                'moodle_pass': password,
                'gr_no': gr_no,
                'n_id': gr_no,
            }

        if not student.moodle_id:
            student_values.update({
                'moodle_id': user.get('id'),
                'moodle_user': user.get('username')
            })
        student_values.update({
            'nationality': self.partner_id.country_id.id or None,
            'place_birth': self.partner_id.city or None,
            'document_number': self.partner_id.vat or None
        })
        student.write(student_values)
        student_course.write({'roll_number': gr_no})
        logger.info("user: {}".format(user))
        enrol_result = moodle.enrol_user(moodle_course.get('id'),
                                         user.get('id'))
        logger.info(enrol_result)
        member_result = moodle.add_group_members(moodle_group.get('id'),
                                                 user.get('id'))
        logger.info(member_result)
        for course in student_course:
            modality.append(course.course_id.modality_id.code)
        if 'ATH' or 'PRS' in modality:
            moodle_cohort = moodle.get_cohort(self.batch_id.code)
            if moodle_cohort is None:
                moodle_cohort = moodle.core_cohort_create_cohorts(self.batch_id.code)
            cohort_member = moodle.core_cohort_add_cohorts_members(moodle_cohort.get('id'), user.get('id'))
            logger.info(cohort_member)
            

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
            # student_user.partner_id.write(details)
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
