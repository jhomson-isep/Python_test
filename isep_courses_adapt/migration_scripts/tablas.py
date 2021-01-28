# -*- coding: utf-8 -*-
from sqlachemy_conn import *
from sqlalchemy import and_

session_pg = get_pg_session()
session_server = get_session_server_isep()


def university_migration():
    universities = session_server.query(
        Tablas.CodItem.label('code'),
        Tablas.NomItem.label('name')).filter(
        and_(Tablas.CodTaula == 'UN', Tablas.NomItem != '')).all()
    for university in universities:
        try:
            op_university = session_pg.query(OpUniversity).filter(
                OpUniversity.code == university.code).first()
            if op_university is None:
                op_university = OpUniversity()
                op_university.code = university.code
                op_university.name = university.name
                session_pg.add(op_university)
                session_pg.commit()
                print("University created: ",
                      [op_university.code, op_university.name])
            else:
                print("University Already exist: ",
                      [op_university.code, op_university.name])
        except Exception as e:
            print(e)
            continue


if __name__ == "__main__":
    university_migration()
