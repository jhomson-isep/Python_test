# -*- coding: utf-8 -*-
from sqlachemy_conn import get_pg_session, get_session_server_isep, OpGdriveDocuments, OpStudent, OpDocumentType, ResPartner
from sqlalchemy import and_
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import base64
import io

lsfiles = os.listdir(path='Folder/')
session_pg = get_pg_session()
session_isep = get_session_server_isep()

def Gauth(self):
    logger.info(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.dirname(os.path.abspath(__file__))
    credentials_file = model_path + "../models/drive/credentials.txt"
    drive_config_file = model_path + '../models/drive/client_secrets.json'
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

def upload_file(self, values):
    gauth = Gauth()
    drive = GoogleDrive(gauth)
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    exist_folder = False
    file = drive.CreateFile()
    folder = ''
    for folders in file_list:
        document = session_pg.query(OpGdriveDocuments).filter(
            OpGdriveDocuments.partner_id == values['partner_id']).first()
        if document is not None:
            if folders['id'] == document.folder_id:
                exist_folder = True
                folder = folders
                break
    if not exist_folder:
        partner = session_pg.query(ResPartner).filter(
            ResPartner.id == values['partner_id']).first()
        name = partner.name
        folder = drive.CreateFile(
            {"title": name, "mimeType": "application/vnd.google-apps.folder"})
        folder.Upload()
    file.content = io.BytesIO(base64.b64decode(values['file']))
    file['title'] = values['filename']
    file['parents'] = [{'id': folder['id']}]
    file.Upload()
    values['folder_id'] = folder['id']
    values['drive_id'] = file['id']
    return values

for file in lsfiles:
    N_Id, document_id, filename = file.split('_', maxsplit=2)
    with open('Folder/'+lsfiles[0], 'rb') as file:
        content_file = base64.b64encode(file.read())
        file.close()

    if not document_id.is_digit():
        filename = document_id + '-' + filename
        document_id = 7
    document_type_isep = session_isep.query(TiposDocumento).filter(
        TiposDocumento.ID == int(document_id)
        ).first()
    document_type = session_pg.query(OpDocumentType).filter(
        OpDocumentType.name == document_type_isep.Nombre
        ).first()
    student = session_pg.query(OpStudent).filter(
        OpStudent.n_id == int(N_Id)
        ).first()
    partner = session_pg.query(ResPartner).filter(
        ResPartner.id == student.partner_id
        ).first()
    document = session_pg.query(OpGdriveDocuments).filter(
        and_(OpGdriveDocuments.document_type_id == OpDocumentType.id,
             OpGdriveDocuments.partner_id == partner.id)
        ).first()
    if document is None:
        pass
    else:
        pass

