# -*- coding: utf-8 -*-
from op_sql import SQL
from connect_postgresql import PSQL
from psycopg2 import DatabaseError, DataError, IntegrityError, OperationalError, ProgrammingError
from pyodbc import Error as ESSQL
from datetime import date, datetime
import base64
import re


def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).
    """
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))


def replace_special_caracter(args):
    s = re.split("'", args)
    args = ''
    for i in s:
        args = args + i
    return args

try:
    sql_server = SQL()
    postgres = PSQL()
    batches = sql_server.get_all_courses()
    for batch in batches:
        try:
            exist_batch = postgres.get_batch_by_code(batch.Curso_Id)
            if exist_batch is None:
                course_id = postgres.get_course_by_code(batch.code)
                partner_id = postgres.get_partner_by_name(batch.Coordinador)
                campus_id = postgres.get_campus_by_name(batch.Marca)
                practices_id = postgres.get_practices_type_by_name(batch.TipoPracticas)
                end_date = batch.FechaFin if batch.FechaFin is not None else add_years(datetime.today().date(), 1)
                fechaInicio = datetime.today().date()
                if batch.FechaInicio is not None:
                    fechaInicio = batch.FechaInicio.date()
                elif batch.FechaAlta is not None:
                    fechaInicio = batch.FechaAlta.date()
                fechaDiplomas = datetime(1900, 1, 1, 0, 0, 0, 0)
                if batch.FechaDiplomas is not None:
                    fechaDiplomas = batch.FechaDiplomas.date()
                    fechaDiplomas = datetime(fechaDiplomas.year, fechaDiplomas.month, fechaDiplomas.day, 0, 0, 0, 0)
                diaSemana = replace_special_caracter(batch.DiaSemana) if batch.DiaSemana is not None else ''
                horario = replace_special_caracter(batch.Horario) if batch.Horario is not None else ''
                lugarClase = replace_special_caracter(batch.LugarClase) if batch.LugarClase is not None else ''
                values = [
                    batch.Curso_Id,
                    batch.Curso_Id,
                    course_id[0] if course_id is not None else '1',
                    fechaInicio,
                    end_date,
                    partner_id[0] if partner_id is not None else 'NULL',
                    campus_id[0] if campus_id is not None else 'NULL',
                    fechaDiplomas,
                    batch.AnyAcademico,
                    diaSemana,
                    horario,
                    lugarClase,
                    batch.LimiteMatriculas,
                    practices_id[0] if practices_id is not None else 'NULL'
                ]
                print(values)
                postgres.create_batch(values)
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