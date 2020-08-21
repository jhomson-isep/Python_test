# -*- coding: utf-8 -*-
from odoo import http

# class CustomName(http.Controller):
#     @http.route('/custom_name/custom_name/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_name/custom_name/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_name.listing', {
#             'root': '/custom_name/custom_name',
#             'objects': http.request.env['custom_name.custom_name'].search([]),
#         })

#     @http.route('/custom_name/custom_name/objects/<model("custom_name.custom_name"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_name.object', {
#             'object': obj
#         })