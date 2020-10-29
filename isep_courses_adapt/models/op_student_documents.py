# -*- coding: utf-8 -*-
from pydrive.drive import GoogleDrive, GoogleDriveFile
from odoo import models, fields, api
from pydrive.auth import GoogleAuth
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

    @api.multi
    def download_file(self):
        gauth = self.Gauth()
        drive = GoogleDrive(gauth)

        file = drive.CreateFile({'id': self.drive_id})
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
    def upload_file(self):
        gauth = self.Gauth()

        drive = GoogleDrive(gauth)
        logger.info(os.path.abspath(self.filename))
        file = drive.CreateFile()
        file.content = io.BytesIO(base64.b64decode(self.file))
        file['title'] = self.filename
        file.Upload()
        self.document_name = self.filename
        self.filename = ''
        self.file = b'\x00'
        self.drive_id = file['id']

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
