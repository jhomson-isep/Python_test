from addons.payment.models.payment_acquirer import _partner_split_name
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from collections import OrderedDict
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
import logging
import base64

from odoo.sql_db import db_connect

logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):
    FIELDS_CREATE = ['document_id', 'file']

    @http.route(['/my/gdrive', '/my/gdrive/documents'], type='http', auth='user', website=True)
    def my_gdrive_documents(self, redirect=None, **post):
        partner = request.env.user.partner_id
        response = request.render("isep_courses_adapt.op_gdrive_documentation",
                                  {
                                      'partner': partner
                                  })
        return response

    @http.route(['/my/gdrive/create'], type='http', auth='user', website=True)
    def my_gdrive_create(self, redirect=None, **post):
        partner = request.env.user.partner_id
        documents_ids = [document for document in request.env['op.document.type'].search([])]
        values = {
            'partner' : partner,
            'documents_ids': documents_ids,
            'error': {},
            'error_message': [],
        }

        if post and request.httprequest.method == 'POST':
            error, error_message = self.gdrive_form_validate(post)
            if not error:
                error, error_message = self.gdrive_validate_document(post)
            values.update({'error': error, 'error_message': error_message})
            if not error:
                values = {
                    'document_type_id' : int(post.get('document_id')),
                    'partner_id': partner.id,
                    'filename' : post.get('file').filename,
                    'file' : base64.b64encode(post.get('file').read()),
                               }
                partner.sudo().write({
                    'document_ids': [(0, 0, values)]
                })
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/gdrive')

        response = request.render("isep_courses_adapt.gdrive_create", values)
        return response

    @http.route(['/my/gdrive/update/<int:id>'], type='http', auth='user', website=True)
    def my_gdrive_update(self, id, redirect=None, **post):
        partner = request.env.user.partner_id
        document_ids = request.env['op.gdrive.documents'].search([('partner_id', '=', partner.id),
                                                                 ('document_type_id', '=', partner.document_ids.document_type_id.id)], limit=1)
        values = {
            'documents_ids' : document_ids,
            'document_type_id' : document_ids.document_type_id,
            'error': {},
            'error_message': [],
        }
        if post and request.httprequest.method == 'POST':
            error, error_message = self.gdrive_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            if not error:
                values = {
                    'document_type_id' : partner.document_ids.document_type_id.id,
                    'partner_id': partner.id,
                    'filename' : post.get('file').filename,
                    'file' : base64.b64encode(post.get('file').read()),
                               }
                partner.sudo().write({
                    'document_ids': [(1, id, values)]
                })
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/gdrive')
        response = request.render("isep_courses_adapt.op_gdrive_update",values)
        return response

    def gdrive_form_validate(self, data):
        error = dict()
        error_message = []

        # Validation
        for field_name in self.FIELDS_CREATE:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # file validation
        if data.get('file').filename == '':
            error["filename"] = 'error'
            error_message.append(_('Select a file'))
        elif data.get('file').filename.lower().split('.')[-1] not in ['png', 'pdf', 'jpeg', 'jpg']:
            error["filename"] = 'error'
            error_message.append(_('Invalid Format of file! Please enter a valid format file.'))
        documents_ids = [document.id for document in request.env['op.document.type'].search([])]
        #document type validation
        if int(data.get('document_id')) not in documents_ids:
            error["document_id"] = "error"
            error_message.append(_('Select a document type!'))

        return error, error_message

    def gdrive_validate_document(self, data):
        error = dict()
        error_message = []
        document_exits = request.env['op.gdrive.documents'].search([('partner_id', '=', request.env.user.partner_id.id),
                                                                    ('document_type_id', '=',
                                                                     int(data.get('document_id')))], limit=1)
        # Document validation
        if document_exits.id:
            error["document_id"] = "error"
            error_message.append(_('Document ' + document_exits.document_type_id.name + ' already exist!'))

        return error, error_message


