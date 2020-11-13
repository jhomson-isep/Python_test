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


try:
    sql_server = SQL()
    postgres = PSQL()
    falcuties = sql_server.get_all_faculties()
    for faculty in falcuties:
        try:
            if faculty.Nombre and faculty.Apellidos and faculty.EMail and faculty.Telefono and  faculty.Direccion \
                    and faculty.CodPostal and faculty.Poblacion and faculty.NIFP is None:
                continue
            exist_faculty = postgres.get_faculty_by_nifp(faculty.NIFP)
            if exist_faculty is None:
                app_country = sql_server.get_country_by_nifp(faculty.NIFP)
                country_id = postgres.get_country_by_name(app_country.country) if app_country is not None else 'NULL'
                partner_id = postgres.get_partner_by_vat(faculty.NIFP)
                if partner_id is None:
                    values = [
                        create_name(faculty.Nombre,
                                         faculty.Apellidos),
                        faculty.EMail if faculty.EMail is not None else '',
                        faculty.Telefono if faculty.Telefono is not None else '',
                        faculty.Telefono if faculty.Telefono is not None else '',
                        faculty.Direccion if faculty.Direccion is not None else '',
                        faculty.CodPostal if faculty.CodPostal is not None else '',
                        faculty.Poblacion if faculty.Poblacion is not None else '',
                        country_id if country_id is not None else 'NULL',
                        faculty.NIFP,
                        False
                    ]
                    print(values)
                    postgres.create_partner(values)
                partner_id = postgres.get_partner_by_vat(faculty.NIFP)
                faculty_values = [
                    faculty.Nombre if faculty.Nombre is not None else '',
                    faculty.Apellidos if faculty.Apellidos is not None else '',
                    datetime.today().date(),
                    'other',
                    country_id,
                    partner_id[0],
                    faculty.NIFP
                ]
                print(faculty_values)
                postgres.create_faculty(faculty_values)
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