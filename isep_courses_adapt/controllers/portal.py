from datetime import date

from odoo import http, _, fields
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.exceptions import AccessError, MissingError
from odoo.http import request, Controller
from odoo.addons.portal.controllers.portal import CustomerPortal, \
    pager as portal_pager, get_records_pager
import logging
import base64

from odoo.osv import expression

logger = logging.getLogger(__name__)


class GoogleDriveController(CustomerPortal):
    FIELDS_CREATE = ['document_id', 'file']

    def _prepare_portal_layout_values(self):
        values = super(GoogleDriveController, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        OpDriveDocuments = request.env['op.gdrive.documents']
        documents_count = OpDriveDocuments.search_count([('partner_id', '=',
                                                          partner.id)])

        values.update({
            'documents_count': documents_count
        })
        return values

    @http.route(['/my/documents', '/my/documents/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_my_documents(self, page=1, date_begin=None, date_end=None,
                            sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        OpDriveDocuments = request.env['op.gdrive.documents']
        documents_ids = [document for document in
                         request.env['op.document.type'].search([])]

        domain = [('partner_id', '=', partner.id)]

        searchbar_sortings = {
            'create_date': {'label': _('Upload date'),
                            'order': 'create_date desc'},
            'document_name': {'label': _('Name'),
                              'order': 'document_name desc'},
            'document_type': {'label': _('Document type'),
                              'order': 'document_type_id desc'},
        }

        # default sort by
        if not sortby:
            sortby = 'create_date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        # count for pager
        documents_count = OpDriveDocuments.search_count(domain)
        print(documents_count)
        # make pager
        pager = portal_pager(
            url="/my/documents",
            url_args={'date_begin': date_begin, 'date_end': date_end,
                      'sortby': sortby},
            total=documents_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        documents = OpDriveDocuments.search(domain, order=sort_order,
                                            limit=self._items_per_page,
                                            offset=pager['offset'])
        request.session['my_documents_history'] = documents.ids[:100]

        values.update({
            'date': date_begin,
            'documents': documents.sudo(),
            'page_name': 'documents',
            'pager': pager,
            'default_url': '/my/documents',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("isep_courses_adapt.portal_my_documents", values)

    @http.route(['/my/documents/<int:document_id>'], type='http',
                auth="public", website=True)
    def portal_document_page(self, document_id, report_type=None,
                          access_token=None, message=False, download=False,
                          **kw):
        try:
            drive_document = self._document_check_access(
                'op.gdrive.documents', document_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        documents_ids = [document for document in
                         request.env['op.document.type'].search([])]

        values = {
            'drive_document': drive_document,
            'message': message,
            'token': access_token,
            'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': drive_document.partner_id.id,
            'report_type': 'html',
        }

        return request.render('isep_courses_adapt.gdrive_create', values)

    @http.route(['/my/documents/update/<int:doc_id>'],
                type='http', auth='user', website=True)
    def portal_document_update(self, doc_id, **post):
        partner = request.env.user.partner_id
        document = request.env['op.gdrive.documents']. \
            search([('id', '=', doc_id)], limit=1)

        values = {
            'doc_id': doc_id,
            'document': document,
            'documents': document,
            'page_name': 'update_document',
            'document_type_id': document.document_type_id,
            'error': {},
            'error_message': [],
        }
        if post and request.httprequest.method == 'POST':
            error, error_message = self.gdrive_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            if not error:
                document_values = {
                    'document_type_id': document.document_type_id.id,
                    'partner_id': partner.id,
                    'filename': post.get('file').filename,
                    'file': base64.b64encode(post.get('file').read()),
                }
                partner.sudo().write({
                    'document_ids': [(1, doc_id, document_values)]
                })
                values.update({
                    'doc_id': doc_id,
                    'document_type_id': document.document_type_id,
                })
                return request.redirect("/my/documents")
        return request.render("isep_courses_adapt.portal_documents_update",
                              values)

    @http.route(['/my/documents/create'], type='http', auth='user',
                website=True)
    def portal_document_create(self, **post):
        partner = request.env.user.partner_id
        documents_ids = [document for document in
                         request.env['op.document.type'].search([])]
        values = {
            'partner': partner,
            'page_name': 'create_document',
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
                values.update({
                    'partner': partner,
                    'documents_ids': documents_ids,
                })
                return request.redirect("/my/documents")
        return request.render("isep_courses_adapt.portal_documents_create",
                              values)

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
                values.update({
                    'partner': partner,
                    'documents_ids': documents_ids,
                    })
        return request.render("isep_courses_adapt.gdrive_create", values)

    @http.route(['/my/gdrive/update/<int:doc_id>'],
                type='http', auth='user', website=True)
    def my_gdrive_update(self, doc_id, **post):
        partner = request.env.user.partner_id
        document_ids = request.env['op.gdrive.documents']. \
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

    @http.route(['/my/gdrive/download/<int:doc_id>'],
                type='http', auth='user', website=True)
    def my_gdrive_download(self, doc_id, **post):
        document_ids = request.env['op.gdrive.documents']. \
            search([('id', '=', doc_id)], limit=1)
        return document_ids.download_file()