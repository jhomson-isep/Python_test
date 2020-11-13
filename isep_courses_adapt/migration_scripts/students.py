# -*- coding: utf-8 -*-
from op_sql import SQL
from connect_postgresql import PSQL
from psycopg2 import DatabaseError, DataError, IntegrityError, OperationalError, ProgrammingError
from pyodbc import Error as ESSQL
from datetime import date, datetime

def create_name(firts, last):
    if firts is None:
        return last
    elif last is None:
        return firts
    else:
        return firts + last

def cupr_or_dni(curp, dni):
    if curp is None:
        return dni
    elif dni is None:
        return curp
    else:
        return ''


try:
    sql_server = SQL()
    postgres = PSQL()
    students = sql_server.get_all_students()
    for student in students:
        try:
            if student.Nombre and student.Apellidos and student.EMail and student.Telefono and student.Direccion \
                and student.CodPostal and student.Poblacion and student.CURPMx and student.DNI and student.N_Id \
                and student.TipoDocumento and student.TipoEstudios and student.Sede \
                    is None:
                continue
            exist_student = postgres.get_sutdent_by_gr_no(student.N_Id)
            if exist_student is None:
                app_country = sql_server.get_country_by_nid(student.N_Id)
                country_id = postgres.get_country_by_name(app_country.country) if app_country is not None else 'NULL'
                partner_id = postgres.get_partner_by_vat(cupr_or_dni(student.CURPMx, student.DNI))
                if partner_id is None:
                    values = [
                        create_name(student.Nombre, student.Apellidos),
                        student.EMail if student.EMail is None else '',
                        student.Telefono if student.Telefono is None else '',
                        student.Telefono if student.Telefono is None else '',
                        student.Direccion if student.Direccion is None else '',
                        student.CodPostal if student.CodPostal is None else '',
                        student.Poblacion if student.Poblacion is None else '',
                        country_id,
                        cupr_or_dni(student.CURPMx, student.DNI),
                        True
                    ]
                    print('Partner:', values)
                    postgres.create_partner(values)
                partner_id = postgres.get_partner_by_vat(cupr_or_dni(student.CURPMx, student.DNI))
                campus_id = postgres.get_campus_by_code(student.Sede)
                document_type_id = postgres.get_document_type_by_code(student.TipoDocumento)
                study_type_id = postgres.get_study_type_by_code(student.TipoEstudios)
                university_id = postgres.get_university_by_code(student.TipoEstudios)
                if student.Sexo == 'H':
                    gender = 'm'
                elif student.Sexo == 'M':
                    gender = 'f'
                else:
                    gender = 'o'
                if student.FechaNacimiento is not None:
                    fechaNacimiento = student.FechaNacimiento.date()
                else:
                    fechaNacimiento = datetime.today().date()
                student_values = [
                    student.Nombre if student.Nombre is not None else '',
                    student.Apellidos if student.Apellidos is not None else '',
                    partner_id[0],
                    fechaNacimiento,
                    country_id,
                    student.N_Id,
                    student.N_Id,
                    campus_id[0] if campus_id is not None else 'NULL',
                    student.CURPMx if student.CURPMx is not None else 'NULL',
                    student.AnyFinalizacionEstudios,
                    document_type_id[0] if document_type_id is not None else 'NULL',
                    student.DNI if student.DNI is not None else 'NULL',
                    study_type_id[0] if study_type_id is not None else 'NULL',
                    university_id[0] if university_id is not None else 'NULL',
                    student.IDMoodle,
                    student.Usuario
                ]
                print('Student:', student_values)
                postgres.create_student(student_values)
        except DataError as de:
            print(de)
            postgres.conn.close()
        except IntegrityError as ie:
            print(ie)
            postgres.conn.close()
        except OperationalError as oe:
            print(oe)
            postgres.conn.close()
        except ProgrammingError as pe:
            print(pe)
            postgres.conn.close()
except DatabaseError as dbe:
    print(dbe)
except ESSQL as e:
    print(e)