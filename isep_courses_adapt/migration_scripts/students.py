# -*- coding: utf-8 -*-
from op_sql import SQL
from connect_postgresql import PSQL
from psycopg2 import DatabaseError, DataError, IntegrityError, OperationalError, ProgrammingError
from pyodbc import Error as ESSQL
from datetime import datetime
from validation import create_name, cupr_or_dni, verify_id, verify_char_field, replace_special_caracter

try:
    sql_server = SQL()
    postgres = PSQL()
    students = sql_server.get_all_students()
    for student in students:
        try:
            if student.Nombre is None and student.Apellidos is None:
                continue
            exist_student = postgres.get_sutdent_by_gr_no(student.N_Id)
            if exist_student is None:
                app_country = sql_server.get_country_by_nid(student.N_Id)
                country_id = postgres.get_country_by_name(app_country.country) if app_country is not None else 'NULL'
                partner_id = postgres.get_partner_by_vat(student.N_Id)
                if partner_id is None:
                    values = [
                        replace_special_caracter(create_name(student.Nombre, student.Apellidos)),
                        replace_special_caracter(verify_char_field(student.EMail)),
                        replace_special_caracter(verify_char_field(student.Telefono)),
                        replace_special_caracter(verify_char_field(student.Telefono)),
                        replace_special_caracter(verify_char_field(student.Direccion)),
                        replace_special_caracter(verify_char_field(student.CodPostal)),
                        replace_special_caracter(verify_char_field(student.Poblacion)),
                        verify_id(country_id),
                        student.N_Id,
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
                    replace_special_caracter(verify_char_field(student.Nombre)),
                    replace_special_caracter(verify_char_field(student.Apellidos)),
                    verify_id(partner_id),
                    fechaNacimiento,
                    gender,
                    verify_id(country_id),
                    student.N_Id,
                    student.N_Id,
                    verify_id(campus_id),
                    verify_id(student.CURPMx),
                    verify_id(student.AnyFinalizacionEstudios),
                    verify_id(document_type_id),
                    replace_special_caracter(verify_char_field(student.DNI)),
                    verify_id(study_type_id),
                    verify_id(university_id),
                    verify_id(student.IDMoodle),
                    replace_special_caracter(verify_char_field(student.Usuario))
                ]
                print('Student:', student_values)
                postgres.create_student(student_values)
            else:
                print("Already exist:", student.N_Id)
        except DataError as de:
            print(de)
            postgres.conn.close()
            break
        except IntegrityError as ie:
            print(ie)
            postgres.conn.close()
            break
        except OperationalError as oe:
            print(oe)
            postgres.conn.close()
            break
        except ProgrammingError as pe:
            print(pe)
            postgres.conn.close()
            break
except DatabaseError as dbe:
    print(dbe)
except ESSQL as e:
    print(e)