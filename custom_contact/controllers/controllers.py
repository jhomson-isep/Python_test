# -*- coding: utf-8 -*-
from odoo import http

# class Extra-addons/customContact(http.Controller):
#     @http.route('/extra-addons/custom_contact/extra-addons/custom_contact/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/extra-addons/custom_contact/extra-addons/custom_contact/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('extra-addons/custom_contact.listing', {
#             'root': '/extra-addons/custom_contact/extra-addons/custom_contact',
#             'objects': http.request.env['extra-addons/custom_contact.extra-addons/custom_contact'].search([]),
#         })

#     @http.route('/extra-addons/custom_contact/extra-addons/custom_contact/objects/<model("extra-addons/custom_contact.extra-addons/custom_contact"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('extra-addons/custom_contact.object', {
#             'object': obj
#         })