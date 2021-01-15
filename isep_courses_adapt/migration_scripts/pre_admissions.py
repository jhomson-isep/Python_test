from datetime import datetime
from sqlalchemy.dialects import mssql
from sqlalchemy import and_, desc
from sqlachemy_conn import *
import traceback

# SQL SERVER SESSION
session_server = get_session_server()
# SQL SERVER AREAS
pre_admissions = session_server.query(GinPrematriculas).order_by(
    GinPrematriculas.FechaPreMatriculacion.desc()).filter(
    GinPrematriculas.ID.in_((77161, 77162))).all()

# ****** print query ******
# pre_admissions = query.all()
# print(query.statement.compile(dialect=mssql.dialect()))
# ****** print query ******

# POSTGRES SERVER SESSION
session_pg = get_pg_session()
for pre_admission in pre_admissions:
    print(pre_admission.ID)
    print(pre_admission.CodigoGrupo)
    try:
        batch = session_pg.query(OpBatch).filter(
            OpBatch.code == pre_admission.CodigoGrupo).first()
        admission_register = session_pg.query(OpAdmissionRegister).filter(
            OpAdmissionRegister.batch_id == batch.id).first()
        partner = session_pg.query(ResPartner).filter(
            ResPartner.email == pre_admission.EMail).first()
        if admission_register is not None and partner is not None:
            application_number = "-".join([batch.code, str(pre_admission.ID)])
            admission = session_pg.query(OpAdmission).filter(
                OpAdmission.application_number == application_number).first()
            if admission is None:
                name = ' '.join([pre_admission.Nombres, pre_admission.Apellidos])
                gender = 'f' if pre_admission.Sexo == 'Mujer' else 'm'
                admission = OpAdmission()
                admission.name = name
                admission.first_name = pre_admission.Nombres
                admission.middle_name = None
                admission.last_name = pre_admission.Apellidos
                admission.birth_date = pre_admission.FechaNacimiento
                admission.gender = gender
                admission.student_id = None
                admission.partner_id = partner.id
                admission.email = partner.email
                admission.phone = partner.phone
                admission.mobile = partner.mobile
                admission.street = partner.street
                admission.city = partner.city
                admission.country_id = partner.country_id
                admission.zip = partner.zip[0:7]
                admission.state_id = partner.state_id
                admission.register_id = admission_register.id
                admission.application_number = application_number
                admission.application_date = pre_admission.FechaMatricula
                admission.admission_date = pre_admission.FechaMatricula
                admission.course_id = admission_register.course_id
                admission.batch_id = batch.id
                admission.unsubscribed_date = None
                admission.academic_record_closing = None
                admission.exam_on_campus = False
                admission.temporary_leave = False
                admission.mexico = False
                admission.mx_documentation = False
                admission.state = 'draft'
                admission.is_student = False
                admission.active = True
                session_pg.add(admission)
                session_pg.commit()
                print("Admission created: ", admission.application_number)
            else:
                print("Admission Already exist: ",
                      admission.application_number)
        else:
            print("Admission register or partner not found")
    except Exception as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        continue
