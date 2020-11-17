# -*- coding: utf-8 -*-
from sqlalchemy import create_engine, or_
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


class GinCurso(Base_server):
    __table__ = Table('gin_Cursos', metadata_server, autoload=True)


#SQL SERVER SESSION
Session_server = sessionmaker()
Session_server.configure(bind=server)
session_server = Session_server()
#SQL SERVER CURSOS
cursos = session_server.query(GinCurso).all()
#POSTGRES SERVER SESSION
Session_pg = sessionmaker()
Session_pg.configure(bind=postgres)
session_pg = Session_pg()

for curso in cursos:
    opcourse = session_pg.query(OpCourse).filter(or_(OpCourse.name == curso.Nombre, OpCourse.code == curso.Codigo)).first()
    if opcourse is None:
        opcourse = OpCourse()
        opcourse.name = curso.Nombre
        opcourse.code = curso.Codigo
        opcourse.active = True
        opcourse.evaluation_type = 'Normal'
        session_pg.add(opcourse)
        session_pg.commit()
        print("Course:", opcourse.code)
    else:
        print("Al ready exist:", opcourse.code)
