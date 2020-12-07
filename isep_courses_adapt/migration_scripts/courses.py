# -*- coding: utf-8 -*-
from sqlalchemy import and_
from sqlachemy_conn import get_session_server, GinAreaCurso, get_pg_session, \
    OpAreaCourse, GinCurso, OpCourse

# SQL SERVER SESSION
session_server = get_session_server()
# SQL SERVER AREAS
areas = session_server.query(GinAreaCurso).all()
# POSTGRES SERVER SESSION
session_pg = get_pg_session()

for area in areas:
    opareacurso = session_pg.query(OpAreaCourse).filter(
        OpAreaCourse.code == area.Codigo).first()
    if opareacurso is None:
        opareacurso = OpAreaCourse()
        opareacurso.code = area.Codigo
        opareacurso.name = area.Nombre
        session_pg.add(opareacurso)
        session_pg.commit()
        print("Area:", opareacurso.code)
    else:
        print("Area Already exist:", opareacurso.code)
areacourses = session_server.query(GinCurso.Codigo.label('code_course'),
                                   GinCurso.Nombre, GinAreaCurso.Codigo.label(
        'code_area')).filter(and_(GinCurso.AreaID == GinAreaCurso.ID,
                                  GinCurso.IdentidadID.in_([1, 68, 69]))).all()
print(areacourses)
for areac in areacourses:
    opareacourse = session_pg.query(OpAreaCourse).filter(
        OpAreaCourse.code == areac.code_area).first()
    if opareacourse is None:
        continue
    opcourse = session_pg.query(OpCourse).filter(
        and_(OpCourse.code == areac.code_course,
             OpCourse.area_id == opareacourse.id)).first()
    if opcourse is None:
        opcourse = OpCourse()
        opcourse.name = areac.Nombre
        opcourse.code = areac.code_course
        opcourse.active = True
        opcourse.evaluation_type = 'Normal'
        opcourse.area_id = opareacourse.id
        session_pg.add(opcourse)
        session_pg.commit()
        print("Course:", opcourse.code)
    else:
        print("Course Already exist:", opcourse.code)
