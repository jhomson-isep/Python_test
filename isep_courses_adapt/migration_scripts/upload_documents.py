
# -*- coding: utf-8 -*-
import os
import base64

lsfiles = os.listdir(path='Folder/')

for file in lsfiles:
    N_Id, document_id, filename = file.split('_', maxsplit=2)
    with open('Folder/'+lsfiles[0], 'rb') as file:
        content_file = base64.b64encode(file.read())
        file.close()

    print("N_Id:", int(N_Id))
    print("document_id:", document_id)
    print("filename:", filename)
    print("Number of files:", len(lsfiles))
    #print("content_file:", content_file)