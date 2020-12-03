from addons.payment.models.payment_acquirer import _partner_split_name
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from collections import OrderedDict
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
import logging

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
        partner_doc_ids = [partner_document for partner_document in
                           request.env['op.gdrive.documents'].search([('partner_id', '=', partner.id)])]
        values = {
            'partner' : partner,
            'documents_ids': documents_ids,
            'partner_doc_ids': partner_doc_ids,
            'error': {},
            'error_message': [],
        }

        if post and request.httprequest.method == 'POST':
            error, error_message = self.gdrive_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            if not error:
                values = {key: post[key] for key in self.FIELDS_CREATE}
                values.update({
                    'partner_id': partner.id,
                    'filename' : post.get('file').filename,
                               })
                partner.sudo().write({
                    'document_ids': [(0, 0, values)]
                })
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/gdrive')

        response = request.render("isep_courses_adapt.gdrive_create", values)
        return response

    def gdrive_form_validate(self, data):
        error = dict()
        error_message = []

        # Validation
        for field_name in self.FIELDS_CREATE:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # email validation
        if data.get('file').filename == '':
            error["filename"] = 'error'
            error_message.append(_('Select a file'))
        elif data.get('file').filename.lower().split('.')[-1] not in ['png', 'pdf', 'jpeg', 'jpg']:
            error["filename"] = 'error'
            error_message.append(_('Invalid Format of file! Please enter a valid format file.'))

        return error, error_message
