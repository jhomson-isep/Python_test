from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
import os
Base_pg = declarative_base()
postgres = create_engine('postgresql+psycopg2://openpg:openpgpwd@localhost:5432/ISPE')
metadata_pg = MetaData(bind=postgres)
driver = 'SQL+Server'  # for Windows
if os.name == "posix":
    driver = 'ODBC+Driver+17+for+SQL+Server'  # for linux
Base_server = declarative_base()
server = create_engine('mssql+pyodbc://sa:Gr5p4mr3@85.118.244.220/GrupoISEPxtra?driver=%s' % driver)
metadata_server = MetaData(bind=server)


class OpCourse(Base_pg):
    __table__ = Table('op_course', metadata_pg, autoload=True)


class OpAreaCourse(Base_pg):
    __table__ = Table('op_area_course', metadata_pg, autoload=True)


class GinAreaCurso(Base_server):
    __table__ = Table('gin_AreasCurso', metadata_server, autoload=True)


class GinCurso(Base_server):
    __table__ = Table('gin_Cursos', metadata_server, autoload=True)


def get_session_server():
    Session_server = sessionmaker()
    Session_server.configure(bind=server)
    session_server = Session_server()
    return session_server

def get_pg_session():
    Session_pg = sessionmaker()
    Session_pg.configure(bind=postgres)
    session_pg = Session_pg()
    return session_pg