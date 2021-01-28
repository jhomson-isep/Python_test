# -*- coding: utf-8 -*-
from sqlachemy_conn import *
import json

session_pg = get_pg_session()
session_server = get_session_server_isep()


def update_students_from_json():
    with open('moodle_campus.json') as json_file:
        data = json.load(json_file)
        for sql_student in data:
            try:
                student = session_pg.query(OpStudent).filter(
                    OpStudent.n_id == str(sql_student['n_id'])).first()
                if student is not None:
                    student.moodle_id = sql_student['id']
                    student.moodle_user = sql_student['username']
                    session_pg.commit()
                    print("Student updated: ", student.n_id)
                else:
                    print("Student not found: ", sql_student['n_id'])
            except Exception as e:
                print(e)
                continue


def update_student_from_sql():
    alumnos = session_server.query(
        Alumnos.N_Id.label('n_id'),
        Alumnos.gix_cgiClienteID.label('cliente_id'),
        Alumnos.Universidad,
        Alumnos.Movil, Alumnos.Telefono).all()
    for alumno in alumnos:
        try:
            student = session_pg.query(OpStudent).filter(
                OpStudent.n_id == str(alumno.n_id)).first()
            university = session_pg.query(OpUniversity).filter(
                OpUniversity.code == alumno.Universidad).first()
            if student is None:
                print("Student not found: ", alumno.n_id)
                continue

            partner = session_pg.query(ResPartner).filter(
                ResPartner.id == student.partner_id).first()
            if partner is not None:
                if partner.mobile == '' or not partner.mobile or \
                        partner.mobile is None:
                    partner.mobile = alumno.Movil
                if partner.phone == '' or not partner.phone or \
                        partner.phone is None:
                    partner.phone = alumno.Telefono or alumno.Movil
            student.cgi_client_id = alumno.cliente_id
            university_id = university.id if university is not None else None
            student.university_id = university_id
            session_pg.commit()
            print("Student updated: ", student.n_id)

        except Exception as e:
            print(e)
            continue


def update_student_use_me():
    students = session_pg.query(OpStudent).all()
    for student in students:
        try:
            alumno = session_server.query(
                Alumnos.N_Id.label('n_id'),
                Alumnos.gix_cgiClienteID.label('cliente_id'),
                Alumnos.Universidad,
                Alumnos.Movil, Alumnos.Telefono).filter(
                Alumnos.N_Id == int(student.n_id)).first()
            if alumno is None:
                print("Student not found: ", student.n_id)
                continue

            university = session_pg.query(OpUniversity).filter(
                OpUniversity.code == alumno.Universidad).first()
            partner = session_pg.query(ResPartner).filter(
                ResPartner.id == student.partner_id).first()
            if partner is not None:
                if partner.mobile == '' or not partner.mobile or \
                        partner.mobile is None:
                    partner.mobile = alumno.Movil
                if partner.phone == '' or not partner.phone or \
                        partner.phone is None:
                    partner.phone = alumno.Telefono or alumno.Movil

            university_id = university.id if university is not None else None
            student.university_id = university_id
            student.cgi_client_id = alumno.cliente_id
            session_pg.commit()
            print("Student updated: ", student.n_id)

        except Exception as e:
            print(e)
            continue


if __name__ == "__main__":
    update_student_use_me()
