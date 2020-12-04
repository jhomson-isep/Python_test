from odoo import http, _
from odoo.http import request, Controller
import logging
import base64

logger = logging.getLogger(__name__)


class GoogleDriveController(Controller):
    FIELDS_CREATE = ['document_id', 'file']

    @http.route(['/my/gdrive/documents'], type='http', auth='user', website=True)
    def my_gdrive_documents(self):
        partner = request.env.user.partner_id
        document_count = request.env['op.gdrive.documents']. \
            search_count([('partner_id', '=', partner.id)])
        return request.render("isep_courses_adapt.op_gdrive_documentation",
                              {
                                  'document_count': document_count,
                                  'partner': partner
                              })

    @http.route(['/my/gdrive/create'], type='http', auth='user', website=True)
    def my_gdrive_create(self, **post):
        partner = request.env.user.partner_id
        documents_ids = [document for document in request.env['op.document.type'].search([])]
        values = {
            'partner': partner,
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
                    'document_type_id': int(post.get('document_id')),
                    'partner_id': partner.id,
                    'filename': post.get('file').filename,
                    'file': base64.b64encode(post.get('file').read()),
                }
                partner.sudo().write({
                    'document_ids': [(0, 0, values)]
                })
        return request.render("isep_courses_adapt.gdrive_create", values)

    @http.route(['/my/gdrive/update/<int:doc_id>'],
                type='http', auth='user', website=True)
    def my_gdrive_update(self, doc_id, **post):
        partner = request.env.user.partner_id
        document_ids = request.env['op.gdrive.documents'].\
            search([('id', '=', doc_id)], limit=1)
        values = {
            'doc_id': doc_id,
            'document_type_id': document_ids.document_type_id,
            'error': {},
            'error_message': [],
        }
        if post and request.httprequest.method == 'POST':
            error, error_message = self.gdrive_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            if not error:
                values = {
                    'document_type_id': document_ids.document_type_id.id,
                    'partner_id': partner.id,
                    'filename': post.get('file').filename,
                    'file': base64.b64encode(post.get('file').read()),
                }
                partner.sudo().write({
                    'document_ids': [(1, doc_id, values)]
                })
                values.update({
                    'doc_id': doc_id,
                    'document_type_id': document_ids.document_type_id,
                })
        return request.render("isep_courses_adapt.op_gdrive_update", values)

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
        documents_ids = [document.id for document in
                         request.env['op.document.type'].search([])]
        # document type validation
        if int(data.get('document_id')) not in documents_ids:
            error["document_id"] = "error"
            error_message.append(_('Select a document type!'))

        return error, error_message

    def gdrive_validate_document(self, data):
        error = dict()
        error_message = []
        partner_id = request.env.user.partner_id.id
        document_id = int(data.get('document_id'))
        document_exits = request.env['op.gdrive.documents']. \
            search([('partner_id', '=', partner_id),
                    ('document_type_id', '=', document_id)], limit=1)
        # Document validation
        if document_exits.id:
            error["document_id"] = "error"
            name = document_exits.document_type_id.name
            message = 'Document ' + name + ' already exist!'
            error_message.append(_(message))

        return error, error_message
