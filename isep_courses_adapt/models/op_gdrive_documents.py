# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import logging
import base64
import io
import os
import time

logger = logging.getLogger(__name__)


class OpGdriveDocuments(models.Model):
    _name = "op.gdrive.documents"
    _description = "Google Drive Documentation"

    document_type_id = fields.Many2one('op.document.type',
                                       string='Document type')
    drive_url = fields.Char(string="Gdrive URL")
    drive_id = fields.Char(string="Gdrive ID")
    document_name = fields.Char(string="Document name")
    file = fields.Binary()
    filename = fields.Char()
    folder_id = fields.Char(string="Gdrive Folder ID")
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')


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
        start = time.time()
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
        res = self.search([('document_type_id', '=', values['document_type_id']),
                           ('partner_id', '=', values['partner_id'])], limit=1).id
        if res != self.id:
            return values
        for folders in file_list:
            if folders['id'] == self.search([('partner_id', '=', values['partner_id'])], limit=1).folder_id:
                exist_folder = True
                folder = folders
                break
        if not exist_folder:
            partner = self.env['res.partner'].search([('id', '=', values['partner_id'])], limit=1)
            name = partner.name + '-' + str(partner.id)
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
        end = time.time()
        print(f"Runtime of the program is {end - start}")
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
        res = super(OpGdriveDocuments, self).create(values)
        return res

    @api.multi
    def write(self, values):
        if 'filename' in values:
            values = self.upload_file(values)
        res = super(OpGdriveDocuments, self).write(values)
        return res

    @api.one
    @api.constrains('document_type_id', 'partner_id')
    def _check_ids(self):
        res = self.search([('document_type_id', '=', self.document_type_id.id), ('partner_id', '=', self.partner_id.id)], limit=1).id
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
        study_faculty_res = self.env['ir.attachment'].search([('res_model', '=', 'op.gdrive.documents')])
        for rec in study_faculty_res:
            rec.unlink()
        partner_res_void = self.env['op.gdrive.documents'].search(
            [('document_type_id', '=', None), ('partner_id', '=', None)])
        for rec in partner_res_void:
            rec.unlink()

    def get_res_partner_id(self, values):
        for res in self:
            model = self.env['ir.model'].search(['model', '=', res.res_model], limit=1)
            model_name = model[0].name
            partner_id = self.env[model_name]

    def unlink(self):
        res = super(OpGdriveDocuments, self).unlink()
        return res
