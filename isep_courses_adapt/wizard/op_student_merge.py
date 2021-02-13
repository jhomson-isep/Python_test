# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class OpStudentMergeWizard(models.TransientModel):
    _name = 'op.student.merge.wizard'
    _description = "Merge Student for selected Student(s)"

    def _get_students(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []

    student_ids = fields.Many2many(
        'op.student', default=_get_students, string='Students')


    def action_merge(self):
        student_original = 0
        students_to_merge = []
        if len(self.student_ids) == 1:
            raise ValidationError(_('Seleccione al menos dos o mas estudiantes para combinar!!'))
        for student in self.student_ids:
            if student_original == 0:
                student_original = student.id
            else:
                students_to_merge.append(student.id)
        self._merge_fields(student_original ,students_to_merge)
    
    def _merge_fields(self, student_original, students_to_merge):
        student = self.env['op.student'].search([('id', '=', student_original)], limit=1)
        values = {
            'partner_id' : student.partner_id,
            'user_id' : student.user_id,
            'category_id' : student.category_id,
            'lang' : student.lang,
            'place_birth' : student.place_birth,
            'birth_date' : student.birth_date,
            'gender' : student.gender,
            'mobile' : student.mobile,
            'email'  : student.email,
            'document_number' : student.document_number,
            'visa_info' : student.visa_info,
            'phone' : student.phone,
            'type' : student.type,
            'street' : student.street,
            'street2' : student.street2,
            'city' : student.city,
            'state_id' : student.state_id,
            'zip' : student.zip,
            'country_id' : student.country_id,
            'emergency_contact': student.emergency_contact,
            'gr_no' : student.gr_no,
            'document_type_id' : student.document_type_id,
            'university_id' : student.university_id,
            'study_type_id' : student.study_type_id,
            'year_end_studies' : student.year_end_studies,
            'sepyc_program' : student.sepyc_program,
            'uvic_program' : student.uvic_program,
            'status_student' : student.status_student,
            'title'  : student.title,
            'first_name' : student.first_name,
            'last_name' : student.last_name,
            'middle_name' : student.middle_name,
            'moodle_user' : student.moodle_user,
            'moodle_pass' : student.moodle_pass
            }
        for student_m in students_to_merge:
            student_to_merge = self.env['op.student'].search([('id', '=', student_m)], limit=1)
            if student_to_merge.partner_id.id == values['partner_id'].id:
                values['partner_id'] = student_to_merge.partner_id
            if student_to_merge.user_id.id == values['user_id'].id: 
                values['user_id'] = student_to_merge.user_id
            if student_to_merge.category_id.id != values['category_id'].id: 
                values['category_id'] = student_to_merge.category_id
            if values['lang'] == '' or values['lang'] != student_to_merge.lang:
                values['lang'] = student_to_merge.lang
            if values['place_birth'] == '' or values['place_birth'] == student_to_merge.place_birth:
                values['place_birth'] = student_to_merge.place_birth
            if values['birth_date'] is not None or values['birth_date'] == student_to_merge.birth_date:
                values['birth_date'] = student_to_merge.birth_date
            if values['gender'] == student_to_merge.gender:
                values['gender'] = student_to_merge.gender
            if values['mobile'] == student_to_merge.mobile or values['mobile'] == '':
                values['mobile'] = student_to_merge.mobile
            if values['email'] == '' or values['email'] != student_to_merge.email:
                values['email'] = student_to_merge.email
            if values['document_number'] == '' or values['document_number'] != student_to_merge.document_number:
                values['document_number'] = student_to_merge.document_number
            if values['visa_info'] != '' or values['visa_info'] != student_to_merge.visa_info:
                values['visa_info'] = student_to_merge.visa_info 
            if values['phone'] != '' or values['phone'] == student_to_merge.phone:
                values['phone'] = student_to_merge.phone
            if values['type'] != student_to_merge.type:
                values['type'] = student_to_merge.type
            if values['street'] != student_to_merge.street:
                values['street'] = student_to_merge.street
            if values['street2'] != student_to_merge.street2:
                values['street2'] = student_to_merge.street2
            if values['city'] != student_to_merge.city:
                values['city'] = student_to_merge.city
            if values['state_id'].id != student_to_merge.state_id.id:
                values['state_id'] = student_to_merge.state_id
            if values['zip'] != student_to_merge.zip:
                values['zip'] = student_to_merge.zip
            if values['country_id'].id != student_to_merge.country_id.id:
                values['country_id'] = student_to_merge.country_id
            if values['emergency_contact'].id != student_to_merge.emergency_contact.id:
                values['emergency_contact'] = student_to_merge.emergency_contact
            if values['gr_no'] == student_to_merge.gr_no:
                values['gr_no'] = student_to_merge.gr_no
            if values['document_type_id'].id != student_to_merge.document_type_id.id:
                values['document_type_id'] = student_to_merge.document_type_id
            if values['university_id'].id != student_to_merge.university_id.id: 
                values['university_id'] = student_to_merge.university_id
            if values['study_type_id'].id != student_to_merge.study_type_id.id:
                values['study_type_id'] = student_to_merge.study_type_id
            if values['year_end_studies'] != student_to_merge.year_end_studies:
                values['year_end_studies'] = student_to_merge.year_end_studies
            if student_to_merge.sepyc_program:
                values['sepyc_program'] = student_to_merge.sepyc_program
            if student_to_merge.uvic_program:
                values['uvic_program'] = student_to_merge.uvic_program 
            values['status_student'] = student_to_merge.status_student
            values['title'] = student_to_merge.title
            values['first_name'] = student_to_merge.first_name
            values['last_name'] = student_to_merge.last_name
            values['middle_name'] = student_to_merge.middle_name
            values['moodle_user'] = student_to_merge.moodle_user
            values['moodle_pass'] = student_to_merge.moodle_pass
            for admission in student_to_merge.admission_ids:
                if admission not in student.admission_ids:
                    student.write({
                    'admission_ids' : [(4,admission.id)]
                    })
            for course in student_to_merge.course_detail_ids:
                if course not in student.course_detail_ids:
                    student.write({
                    'course_detail_ids' : [(4,course.id)]
                    })
            for document in student_to_merge.document_ids:
                if document not in student.document_ids:
                    student.write({
                    'document_ids' : [(4,document.id)]
                    })
            for access in student_to_merge.access_ids:
                if access not in student.access_ids:
                    student.write({
                    'access_ids' : [(4,access.id)]
                    })
            for course_type in student_to_merge.type_of_course_taken:
                if course_type not in student.type_of_course_taken:
                    student.write({
                        'type_of_course_taken': [
                            (4, student_to_merge.type_of_course_taken.id)]
                    })
            student_to_merge.write({
                'active': False
            })
        values.update({
            'partner_id' :values['partner_id'].id,
            'user_id' : values['user_id'].id,
            'category_id' : values['category_id'].id,
            'state_id' : values['state_id'].id,
            'country_id' : values['country_id'].id,
            'emergency_contact': values['emergency_contact'].id,
            'document_type_id' : values['document_type_id'].id,
            'university_id' : values['university_id'].id,
            'study_type_id' : values['study_type_id'].id,
            'title' : values['title'].id
            })
        student.write(values)
