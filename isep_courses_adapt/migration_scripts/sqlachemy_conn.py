from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
import os

load_dotenv(find_dotenv())

Base_pg = declarative_base()
dbname = os.environ['DATABASE']
user = os.environ['PSQL_USER']
password = os.environ['PSQL_PASSWORD']
host = os.environ['HOST_IP']
port = os.environ['PORT']

postgres = create_engine('postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}'.format(
    user, password, host, port, dbname))

metadata_pg = MetaData(bind=postgres)
driver = 'SQL+Server'  # for Windows
if os.name == "posix":
    driver = 'ODBC+Driver+17+for+SQL+Server'  # for linux
Base_server = declarative_base()
server = create_engine('mssql+pyodbc://sa:Gr5p4mr3@85.118.244.220'
                       ':1433/GrupoISEPxtra?driver=%s' % driver)
server_isep = create_engine('mssql+pyodbc://sa:Gr5p4mr3@85.118.244.220'
                       ':1433/ISEP?driver=%s' % driver)
metadata_server = MetaData(bind=server)
metadata_server_isep = MetaData(bind=server_isep)

#PostgresSQL Tables
class OpCourse(Base_pg):
    __table__ = Table('op_course', metadata_pg, autoload=True)


class OpAreaCourse(Base_pg):
    __table__ = Table('op_area_course', metadata_pg, autoload=True)


class ResPartner(Base_pg):
    __table__ = Table('res_partner', metadata_pg, autoload=True)


class OpStudent(Base_pg):
    __table__ = Table('op_student', metadata_pg, autoload=True)


class OpFaculty(Base_pg):
    __table__ = Table('op_faculty', metadata_pg, autoload=True)


class OpGdriveDocuments(Base_pg):
    __table__ = Table('op_gdrive_documents', metadata_pg, autoload=True)


class OpDocumentType(Base_pg):
    __table__ = Table('op_document_type', metadata_pg, autoload=True)


class OpAttendanceRegister(Base_pg):
    __table__ = Table('op_attendance_register', metadata_pg, autoload=True)


class OpAttendanceSheet(Base_pg):
    __table__ = Table('op_attendance_sheet', metadata_pg, autoload=True)


class OpAttendanceLine(Base_pg):
    __table__ = Table('op_attendance_line', metadata_pg, autoload=True)


class OpBatch(Base_pg):
    __table__ = Table('op_batch', metadata_pg, autoload=True)


#SQL Server Tables
class OpBatch(Base_pg):
    __table__ = Table('op_batch', metadata_pg, autoload=True)


class OpSubject(Base_pg):
    __table__ = Table('op_subject', metadata_pg, autoload=True)


class OpBatchSubjectRel(Base_pg):
    __table__ = Table('op_batch_subject_rel', metadata_pg, autoload=True)


class OpAdmissionRegister(Base_pg):
    __table__ = Table('op_admission_register', metadata_pg, autoload=True)


class OpAdmission(Base_pg):
    __table__ = Table('op_admission', metadata_pg, autoload=True)


class OpExam(Base_pg):
    __table__ = Table('op_exam', metadata_pg, autoload=True)


class OpExamType(Base_pg):
    __table__ = Table('op_exam_type', metadata_pg, autoload=True)


class OpExamSession(Base_pg):
    __table__ = Table('op_exam_session', metadata_pg, autoload=True)


class OpExamAttendees(Base_pg):
    __table__ = Table('op_exam_attendees', metadata_pg, autoload=True)


# SQL Server Tables
class GinAreaCurso(Base_server):
    __table__ = Table('gin_AreasCurso', metadata_server, autoload=True)


class GinCurso(Base_server):
    __table__ = Table('gin_Cursos', metadata_server, autoload=True)


class TiposDocumento(Base_server):
    __table__ = Table('TiposDocumento', metadata_server_isep, autoload=True)


class Asistencias(Base_server):
    __table__ = Table('Asistencias', metadata_server_isep, autoload=True)
class Matriculaciones(Base_server):
    __table__ = Table('Matriculaciones', metadata_server_isep, autoload=True)


def get_session_server():
    Session_server = sessionmaker()
    Session_server.configure(bind=server)
    return Session_server()


def get_session_server_isep():
    Session_server = sessionmaker()
    Session_server.configure(bind=server_isep)
    return Session_server()


def get_pg_session():
    Session_pg = sessionmaker()
    Session_pg.configure(bind=postgres)
    return Session_pg()
