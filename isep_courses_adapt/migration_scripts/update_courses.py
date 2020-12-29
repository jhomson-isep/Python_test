# -*- coding: utf-8 -*-
from sqlalchemy import and_, func
from sqlachemy_conn import *

session_pg = get_pg_session()
session_sql = get_session_server_isep()

courses = session_pg.query(OpCourse).all()
course = courses

for course in courses:
    try:
        course_isep = session_sql.query(IsepCursos.Modalidad.label('modality'),
                                        IsepCursos.TitolCat.label('catalan'),
                                        IsepCursos.Reconeixements,
                                        IsepCursos.Reconocimientos,
                                        IsepCursos.Curso_Id).filter(
            and_(IsepCursos.Modalidad != None, IsepCursos.TitolCat != None,
                 IsepCursos.Reconeixements != None,
                 IsepCursos.Reconeixements != '',
                 IsepCursos.Reconocimientos != None,
                 IsepCursos.Reconocimientos != '',
                 func.substring(IsepCursos.Curso_Id, 3, 2) ==
                 course.code)).first()
        if course_isep is not None:
            modality = session_pg.query(OpModality).filter(
                OpModality.code == course_isep.modality).first()

            if course.modality_id is None:
                course.modality_id = modality.id or None
            if course.name_catalan is None:
                course.name_catalan = course_isep.catalan
            if course.acknowledgments is None:
                course.acknowledgments = course_isep.Reconocimientos
            if course.reconeixements is None:
                course.reconeixements = course_isep.Reconeixements
            session_pg.commit()
            print("Course updated: ", [course.code, course.modality_id,
                                       course.name_catalan,
                                       course.acknowledgments,
                                       course.reconeixements])
        else:
            print("Course {} not found".format(course.code))
    except Exception as e:
        print(e)
        continue
