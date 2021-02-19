from datetime import date

from odoo import http, _, fields
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.exceptions import AccessError, MissingError
from odoo.http import request, Controller, content_disposition
from odoo.addons.portal.controllers.portal import CustomerPortal, \
    pager as portal_pager, get_records_pager
import logging

logger = logging.getLogger(__name__)


class PracticesController(http.Controller):
    @http.route(['/practices'], type='http', auth='public', website=True)
    def my_practices(self, **kw):
        return http.request.render('isep_practices.practice_submenu')

    @http.route(['/my/practices'], type='http', auth='public', website=True)
    def my_practices_create(self, **kw):
        admission = [admission for admission in request.env['op.admission'].search([])]
        admissions =admission
        center = [center for center in request.env['res.partner'].sudo().search([])]
        center_id = [centers for centers in center if centers.center == True]
        tutor = [tutor for tutor in request.env['res.partner'].sudo().search([])]
        tutor_id = [tutors for tutors in tutor if tutors.tutor == True]
        student=''
        if kw:
            print(kw['document_number'])
            students = [students for students in request.env['op.student'].search([])]
            student_unique =[student for student in students if student.document_number==kw['document_number']]
            if len(student_unique):
                student = student_unique
                admissions = [admissions for admissions in admission if admissions.student_id.id == student[0].id]
            else:
                student = 'invalid'
        print(center)
        value = {'center': center_id, 'tutor': tutor_id,'student': student, 'admissions': admissions}
        return http.request.render('isep_practices.my_practices_form', value)


