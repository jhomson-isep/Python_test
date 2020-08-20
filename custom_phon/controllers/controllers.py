# -*- coding: utf-8 -*-
from odoo import http

# class CustomPhon(http.Controller):
#     @http.route('/custom_phon/custom_phon/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_phon/custom_phon/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_phon.listing', {
#             'root': '/custom_phon/custom_phon',
#             'objects': http.request.env['custom_phon.custom_phon'].search([]),
#         })

#     @http.route('/custom_phon/custom_phon/objects/<model("custom_phon.custom_phon"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_phon.object', {
#             'object': obj
#         })