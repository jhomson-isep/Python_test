# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import logging
import base64
import io
import os

logger = logging.getLogger(__name__)


class OpStudentDocuments(models.Model):
    _name = "op.student.documents"
    _description = "Google Drive Documentation"

    document_type_id = fields.Many2one('op.document.type',
                                       string='Document type')
    student_id = fields.Many2one(comodel_name="op.student", string="Student")
    drive_url = fields.Char(string="Gdrive URL")
    drive_id = fields.Char(string="Gdrive ID")
    document_name = fields.Char(string="Document name")
    faculty_id = fields.Many2one(comodel_name="op.faculty", string="Faculty")
    file = fields.Binary()
    filename = fields.Char()
    folder_id = fields.Char(string="Gdrive Folder ID")

    @api.multi
    def download_file(self):
        gauth = self.Gauth()
        drive = GoogleDrive(gauth)

        file = drive.CreateFile({'id': self.drive_id, 'parents' : [{'id': self.folder_id}] })
        logger.info("*******************")
        logger.info(file)

        file.FetchContent(file['mimeType'], False)
        file_gtf = base64.b64encode(file.content.getvalue())
        logger.info(file_gtf)
        self.document_name = file['title']
        attachment = self.env['ir.attachment'].create({
            'name': file['title'],
            'type': 'binary',
            'datas': file_gtf,
            'datas_fname': file['title'],
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': file['mimeType']
        })
        logger.info("atachment_id: {0}".format(attachment.id))
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{0}?download=true'.format(
                attachment.id),
            'target': 'new',
            'nodestroy': False,
        }

    @api.multi
    def upload_file(self, values):
        gauth = self.Gauth()
        self.valid_file(values)
        drive = GoogleDrive(gauth)
        model_path = os.path.dirname(os.path.abspath(__file__))
        file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        exist_folder = False
        file = drive.CreateFile()
        folder = ''
        name = ''
        field = ''
        if 'student_id' in values:
            field = 'student_id'
            model = 'op.student'
        elif 'faculty_id' in values:
            field = 'faculty_id'
            model = 'op.faculty'
        if 'student_id' in values:
            res = self.search([('document_type_id', '=', values['document_type_id']), ('student_id', '=', values['student_id'])], limit=1).id
        elif 'faculty_id' in values:
            res = self.search([('document_type_id', '=', values['document_type_id']), ('faculty_id', '=', values['faculty_id'])], limit=1).id
        if res != self.id:
            return values
        for folders in file_list:
            if folders['id'] == self.search([(field, '=', values[field])], limit=1).folder_id:
                exist_folder = True
                folder = folders
                break
        if not exist_folder:
            name = self.env[model].search([('id', '=', values[field])], limit=1).name
            folder = drive.CreateFile(
                {"title": name, "mimeType": "application/vnd.google-apps.folder"})
            folder.Upload()
        file.content = io.BytesIO(base64.b64decode(values['file']))
        file['title'] = values['filename']
        file['parents'] = [{'id': folder['id']}]
        file.Upload()
        values['document_name'] = values['filename']
        values['file'] = b''
        values['folder_id'] = folder['id']
        values['drive_id'] = file['id']
        return values

    @api.multi
    def Gauth(self):
        logger.info(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.dirname(os.path.abspath(__file__))
        credentials_file = model_path + "/drive/credentials.txt"
        drive_config_file = model_path + '/drive/client_secrets.json'
        GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = drive_config_file
        gauth = GoogleAuth()
        # Try to load saved client credentials
        gauth.LoadCredentialsFile(credentials_file)
        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved credentials
            gauth.Authorize()
        # Save the current credentials to a file
        gauth.SaveCredentialsFile(credentials_file)
        return gauth

    @api.multi
    def valid_file(self, values):
        if values['filename'] == '':
            raise ValidationError(_('Select a file!'))
        if values['filename'].lower().split('.')[-1] in ['png', 'pdf', 'jpeg', 'jpg']:
            return
        else:
            raise ValidationError(_('Invalid format file!.'))

    @api.model
    def create(self, values):
        if 'filename' in values:
            values = self.upload_file(values)
        res = super(OpStudentDocuments, self).create(values)
        return res

    @api.multi
    def write(self, values):
        if 'filename' in values:
            values = self.upload_file(values)
        res = super(OpStudentDocuments, self).create(values)
        return res

    @api.one
    @api.constrains('document_type_id', 'student_id', 'faculty_id')
    def _check_ids(self):
        if self.student_id.id:
            res = self.search([('document_type_id', '=', self.document_type_id.id), ('student_id', '=', self.student_id.id)], limit=1).id
        elif self.faculty_id.id:
            res = self.search([('document_type_id', '=', self.document_type_id.id), ('faculty_id', '=', self.faculty_id.id)], limit=1).id
        if res != self.id:
            gauth = self.Gauth()
            drive = GoogleDrive(gauth)
            file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
            for folders in file_list:
                if folders['id'] == self.search([('id', '=', res)], limit=1).folder_id:
                    folders.Delete()
                    break
            raise ValidationError(_('One documet type per person!!'))

    @api.model
    def delete_void_records(self):
        study_faculty_res = self.env['ir.attachment'].search([('res_model', '=', 'op.student.documents')])
        for rec in study_faculty_res:
            rec.unlink()
        study_faculty_res_void = self.env['op.student.documents'].search(
            [('document_type_id', '=', None), ('student_id', '=', None), ('faculty_id', '=', None)])
        for rec in study_faculty_res_void:
            rec.unlink()
