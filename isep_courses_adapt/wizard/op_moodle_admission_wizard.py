from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
from odoo.addons.isep_courses_adapt.models import moodle
<<<<<<< HEAD
from datetime import datetime
from dateutil.relativedelta import relativedelta
=======
>>>>>>> origin/feature/321-cohorts-moodle
import logging

logger = logging.getLogger(__name__)


class OpMoodleAdmissionWizard(models.TransientModel):
    _name = "op.moodle.admission.wizard"
    _description = "Moodle Admission Wizard"

<<<<<<< HEAD
    @api.onchange('category_id')
    def _get_domain(self):      
        return [('id', '=', str(self.category_id.course_id))]
    
    def _get_admission(self):
        admission_id = self.env.context.get('active_ids', []) or []
        admission = self.env['op.admission'].search([('id', '=', admission_id)])
        return admission
    
    category_id = fields.Many2one('op.moodle.category.rel',
                                  string="Select a Category")
    course_id = fields.Many2many('op.course',
                                 domain=_get_domain,
                                 string="Select a Course")

    @api.multi
    def enroll_student(self):
        print("enroll")
        
        
    # def enroll_student(self):
    #     for record in self:
    #         if record.register_id.max_count:
    #             total_admission = self.env['op.admission'].search_count(
    #                 [('register_id', '=', record.register_id.id),
    #                  ('state', '=', 'done')])
    #             if not total_admission < record.register_id.max_count:
    #                 msg = 'Max Admission In Admission Register :- (%s)' % (
    #                     record.register_id.max_count)
    #                 raise ValidationError(_(msg))

    #         student = self.env['op.student'].search(
    #             [('email', '=', record.email)], limit=1)
    #         if len(student) > 0:
    #             record.student_id = student.id

    #         print(len(student))
    #         print(record.student_id)

    #         if not record.student_id:
    #             vals = record.get_student_vals()
    #             record.partner_id = vals.get('partner_id')
    #             record.student_id = student_id = self.env[
    #                 'op.student'].create(vals).id
    #         else:
    #             student_id = record.student_id.id
    #             record.student_id.write({
    #                 'course_detail_ids': [[0, False, {
    #                     'course_id':
    #                         record.course_id and record.course_id.id or False,
    #                     'batch_id':
    #                         record.batch_id and record.batch_id.id or False,
    #                 }]],
    #             })
    #         if record.fees_term_id:
    #             val = []
    #             product_id = record.register_id.product_id.id
    #             for line in record.fees_term_id.line_ids:
    #                 no_days = line.due_days
    #                 per_amount = line.value
    #                 amount = (per_amount * record.fees) / 100
    #                 date = (datetime.today() + relativedelta(
    #                     days=no_days)).date()
    #                 dict_val = {
    #                     'fees_line_id': line.id,
    #                     'amount': amount,
    #                     'fees_factor': per_amount,
    #                     'date': date,
    #                     'product_id': product_id,
    #                     'state': 'draft',
    #                 }
    #                 val.append([0, False, dict_val])
    #             record.student_id.write({
    #                 'fees_detail_ids': val
    #             })
    #         record.write({
    #             'nbr': 1,
    #             'state': 'done',
    #             'admission_date': fields.Date.today(),
    #             'student_id': student_id,
    #             'is_student': True,
    #         })
    #         reg_id = self.env['op.subject.registration'].create({
    #             'student_id': student_id,
    #             'batch_id': record.batch_id.id,
    #             'course_id': record.course_id.id,
    #             'min_unit_load': record.course_id.min_unit_load or 0.0,
    #             'max_unit_load': record.course_id.max_unit_load or 0.0,
    #             'state': 'draft',
    #         })
    #         reg_id.get_subjects()
    #         record.create_moodle_user()
    
    # def create_moodle_user(self):
    #     moodle = moodle.MoodleLib()
    #     student = self.env['op.student'].search(
    #         [('id', '=', self.student_id.id)], limit=1)
    #     student_course = self.env['op.student.course'].search(
    #         [('student_id', '=', student.id),
    #          ('batch_id', '=', self.batch_id.id)])
    #     logger.info("Student id: {}".format(student.id))
    #     moodle_course = moodle.get_course(self.batch_id.moodle_code)
    #     modality = list()
    #     moodle_cohort = None
    #     logger.info("moodle_course: {}".format(moodle_course))
    #     moodle_group = moodle.get_group(moodle_course.get('id'),
    #                                     self.batch_id.code)
    #     if moodle_group is None:
    #         moodle_group = moodle.core_group_create_groups(
    #             self.batch_id.code, moodle_course.get('id'))
    #     logger.info("moodle_group: {}".format(moodle_group))
    #     password = self.password_generator(length=10)
    #     user = moodle.get_user_by_field(field="email",
    #                                     value=self.partner_id.email.lower())
    #     if student.gr_no:
    #         gr_no = student.gr_no
    #     else:
    #         gr_no = self.env['ir.sequence'].next_by_code('op.gr.number') or '0'

    #     student_values = {}
    #     if user is None:
    #         first_name = self.first_name
    #         if self.middle_name:
    #             first_name = ' '.join([first_name, self.middle_name])

    #         user_response = moodle.create_users(
    #             firstname=first_name,
    #             lastname=self.last_name,
    #             dni=self.partner_id.vat,
    #             password=password,
    #             email=self.partner_id.email.lower())
    #         user = user_response[0]
    #         logger.info(gr_no)
    #         student_values = {
    #             'moodle_id': user.get('id'),
    #             'moodle_user': self.partner_id.email,
    #             'moodle_pass': password,
    #             'gr_no': gr_no,
    #             'n_id': gr_no,
    #         }
    #     else:
    #         user_password = moodle.update_user_password(
    #             user_id=user.get('id'),
    #             password=password)
    #         student_values = {
    #             'moodle_user': user.get('username'),
    #             'moodle_pass': password
    #         }

    #     if not student.moodle_id:
    #         student_values.update({
    #             'moodle_id': user.get('id'),
    #             'moodle_user': user.get('username')
    #         })
    #     student_values.update({
    #         'nationality': self.partner_id.country_id.id or None,
    #         'place_birth': self.partner_id.city or None,
    #         'document_number': self.partner_id.vat or None
    #     })
    #     student.write(student_values)
    #     student_course.write({'roll_number': gr_no})
    #     logger.info("user: {}".format(user))
    #     enrol_result = moodle.enrol_user(moodle_course.get('id'),
    #                                      user.get('id'))
    #     logger.info(enrol_result)
    #     member_result = moodle.add_group_members(moodle_group.get('id'),
    #                                              user.get('id'))
    #     logger.info(member_result)
    #     # for course in student_course:
    #     #     modality.append(course.course_id.modality_id.code)
    #     if 'ATH' or 'PRS' in self.batch_id.code:
    #         print("group: ", self.batch_id.code)
    #         moodle_cohort = moodle.get_cohort(self.batch_id.code)
    #         if moodle_cohort is None:
    #             moodle_cohort = moodle.core_cohort_create_cohorts(
    #                 self.batch_id.code)
    #         cohort_member = moodle.core_cohort_add_cohorts_members(
    #             moodle_cohort.get('id'), user.get('id'))
    #         logger.info(cohort_member)
    
    # def get_student_vals(self):
    #     for student in self:
    #         student_user = self.env['res.users'].search(
    #             [('login', '=', student.email)], limit=1)
    #         if len(student_user) == 0:
    #             student_user = self.env['res.users'].create({
    #                 'name': student.name,
    #                 'login': student.email,
    #                 'image': self.image or False,
    #                 'is_student': True,
    #                 'groups_id': [
    #                     (6, 0,
    #                      [self.env.ref('base.group_portal').id])]
    #             })
    #         details = {
    #             'phone': student.phone,
    #             'mobile': student.mobile,
    #             'email': student.email,
    #             'street': student.street,
    #             'street2': student.street2,
    #             'city': student.city,
    #             'country_id':
    #                 student.country_id and student.country_id.id or False,
    #             'state_id': student.state_id and student.state_id.id or False,
    #             'image': student.image,
    #             'zip': student.zip,
    #         }
    #         # student_user.partner_id.write(details)
    #         details.update({
    #             'title': student.title and student.title.id or False,
    #             'first_name': student.first_name,
    #             'middle_name': student.middle_name,
    #             'last_name': student.last_name,
    #             'birth_date': student.birth_date,
    #             'gender': student.gender,
    #             'course_id':
    #                 student.course_id and student.course_id.id or False,
    #             'batch_id':
    #                 student.batch_id and student.batch_id.id or False,
    #             'image': student.image or False,
    #             'course_detail_ids': [[0, False, {
    #                 'date': fields.Date.today(),
    #                 'course_id':
    #                     student.course_id and student.course_id.id or False,
    #                 'batch_id':
    #                     student.batch_id and student.batch_id.id or False,
    #             }]],
    #             'user_id': student_user.id,
    #             'partner_id': student_user.partner_id.id,
    #         })
    #         return details

    
=======
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
>>>>>>> origin/feature/321-cohorts-moodle
