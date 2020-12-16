# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import and_, desc
from sqlachemy_conn import *

# SQL SERVER SESSION
session_server = get_session_server_isep()
# SQL SERVER AREAS
matriculaciones = session_server.query(Matriculaciones).all()
# POSTGRES SERVER SESSION
session_pg = get_pg_session()

for matricula in matriculaciones:
    print("Matricula: {}".format(matricula.Curso_Id))
    batch = session_pg.query(OpBatch).filter(
        OpBatch.code == matricula.Curso_Id).first()
    admission_register = session_pg.query(OpAdmissionRegister).filter(
        OpAdmissionRegister.batch_id == batch.id).first()
    student = session_pg.query(OpStudent).filter(
        OpStudent.n_id == str(matricula.N_Id)).first()

    if admission_register is not None and student is not None:
        partner = session_pg.query(ResPartner).filter(
            ResPartner.id == student.partner_id).first()
        application_number = "-".join([batch.code, str(matricula.N_Id)])
        admission = session_pg.query(OpAdmission).filter(
            OpAdmission.application_number == application_number).first()

        if admission is None:
            # If the dates are less than 1901, it indicates that they have not
            # been established, so we will leave them in None
            academic_record_closing = None
            unsubscribed_date = None
            if matricula.FechaCierreExpAcademico > datetime(1901, 1, 1):
                academic_record_closing = matricula.FechaCierreExpAcademico
            if matricula.FechaBaja > datetime(1901, 1, 1):
                unsubscribed_date = matricula.FechaBaja
            # boolean fields that are char in the allocation, need to be
            # evaluated for odoo
            exam_on_campus = matricula.HaceExamenesEnCampusVirtual == 1
            temporary_leave = matricula.BajaTemporal == 1
            mexico = matricula.Mexico == 'Si'
            mx_documentation = matricula.DocumentacionMx == 1
            # the name is required, so we must assign depending on the
            # composition of the student
            name = ''
            if not student.middle_name:
                name = str(student.first_name) + " " + str(student.last_name)
            else:
                name = str(student.first_name) + " " + str(
                    student.middle_name) + " " + str(student.last_name)
            # admission values
            admission = OpAdmission()
            admission.name = name
            admission.first_name = student.first_name
            admission.middle_name = student.middle_name
            admission.last_name = student.last_name
            admission.birth_date = student.birth_date
            admission.gender = student.gender
            admission.student_id = student.id
            admission.partner_id = partner.id
            admission.email = partner.email
            admission.phone = partner.phone
            admission.mobile = partner.mobile
            admission.street = partner.street
            admission.city = partner.city
            admission.country_id = partner.country_id
            admission.zip = partner.zip
            admission.state_id = partner.state_id
            admission.register_id = admission_register.id
            admission.application_number = application_number
            admission.application_date = matricula.FechaMatricula
            admission.admission_date = matricula.FechaMatricula
            admission.course_id = admission_register.course_id
            admission.batch_id = batch.id
            admission.unsubscribed_date = unsubscribed_date
            admission.academic_record_closing = academic_record_closing
            admission.exam_on_campus = exam_on_campus
            admission.due_date = matricula.FechaVencimiento
            admission.temporary_leave = temporary_leave
            admission.mexico = mexico
            admission.generation = matricula.GeneracionMx
            admission.mx_documentation = mx_documentation
            admission.observations = matricula.Observaciones
            admission.state = 'draft'
            admission.is_student = True
            admission.active = True
            session_pg.add(admission)
            session_pg.commit()
            print("Admission created: ", admission.application_number)
        else:
            print("Admission Already exist: ", admission.application_number)
    else:
        print("Admission register or student not found")
