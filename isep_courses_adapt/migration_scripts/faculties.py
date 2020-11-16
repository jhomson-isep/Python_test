# -*- coding: utf-8 -*-
from op_sql import SQL
from connect_postgresql import PSQL
from psycopg2 import DatabaseError, DataError, IntegrityError, OperationalError, ProgrammingError
from pyodbc import Error as ESSQL
from datetime import date, datetime
from validation import create_name, verify_char_field, verify_id, replace_special_caracter

try:
    sql_server = SQL()
    postgres = PSQL()
    falcuties = sql_server.get_all_faculties()
    for faculty in falcuties:
        try:
            exist_faculty = postgres.get_faculty_by_nifp(faculty.NIFP)
            if exist_faculty is None:
                app_country = sql_server.get_country_by_nifp(faculty.NIFP)
                country_id = postgres.get_country_by_name(app_country.country) if app_country is not None else 'NULL'
                partner_id = postgres.get_partner_by_vat(faculty.NIFP)
                if partner_id is None:
                    values = [
                        replace_special_caracter(create_name(faculty.Nombre,
                                                             faculty.Apellidos)),
                        replace_special_caracter(verify_char_field(faculty.EMail)),
                        replace_special_caracter(verify_char_field(faculty.Telefono)),
                        replace_special_caracter(verify_char_field(faculty.Telefono)),
                        replace_special_caracter(verify_char_field(faculty.Direccion)),
                        replace_special_caracter(verify_char_field(faculty.CodPostal)),
                        replace_special_caracter(verify_char_field(faculty.Poblacion)),
                        verify_id(country_id),
                        replace_special_caracter(verify_char_field(faculty.NIFP)),
                        False
                    ]
                    print("Partner:", values)
                    postgres.create_partner(values)
                partner_id = postgres.get_partner_by_vat(faculty.NIFP)
                faculty_values = [
                    replace_special_caracter(verify_char_field(faculty.Nombre)),
                    replace_special_caracter(verify_char_field(faculty.Apellidos)),
                    datetime.today().date(),
                    'other',
                    verify_id(country_id),
                    verify_id(partner_id),
                    replace_special_caracter(verify_char_field(faculty.NIFP))
                ]
                print("Faculty:", faculty_values)
                postgres.create_faculty(faculty_values)
            else:
                print("Already exist:", faculty.NIFP)
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
