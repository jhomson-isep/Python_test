from datetime import date

from odoo import http, _, fields
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.exceptions import AccessError, MissingError
from odoo.http import request, Controller, content_disposition
from odoo.addons.portal.controllers.portal import CustomerPortal, \
    pager as portal_pager, get_records_pager
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import logging
import base64
import threading

from odoo.osv import expression

logger = logging.getLogger(__name__)


class AttendancesController(http.Controller):
    @http.route(['/attendances'], type='http', auth='public', website=True)
    def my_attendances(self, **kw):
        return http.request.render('isep_portal_attendances.attendance_link')

    @http.route(['/my/attendances'], type='http', auth='public', website=True)
    def my_attendances_list(self, **kw):
        Employe = http.request.env['hr.employee']
        print(Employe.search([]))
        return http.request.render('isep_portal_attendances.attendance', {
            'employes': Employe.search([])
        })
    @http.route(['/pin/<int:employ_id>'], type='http', auth='public', website=True)
    def my_attendances_frontend(self, employ_id, **kw):
        print("ID:",employ_id)
        return http.request.render('isep_portal_attendances.attendance_create')

    @http.route(['/my/attendance/create'], type='http', auth='public',
                website=True)
    def portal_attendance_create(self, **kw):
        print(kw)
        request.env["hr.attendance"].sudo().create(kw)

                #return request.redirect("/my/documents")
        return request.render("isep_courses_adapt.attendance_create")



