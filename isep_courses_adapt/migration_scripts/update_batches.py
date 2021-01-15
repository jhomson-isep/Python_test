# -*- coding: utf-8 -*-

from sqlalchemy import and_, desc, or_
from sqlachemy_conn import *
from moodle import *

session_pg = get_pg_session()
session_sql = get_session_server_isep()
Moodle = MoodleLib()

courses = session_sql.query(IsepCursos).filter(
    IsepCursos.MoodleId != None).all()

for course in courses:
    try:
        batch = session_pg.query(OpBatch).filter(
            OpBatch.code == course.Curso_Id).first()
        moodle_course = Moodle.get_course(name=course.MoodleId.strip())

        if batch is not None and len(moodle_course) > 0:
            batch.moodle_id = moodle_course.get('id')
            batch.moodle_code = course.MoodleId.strip()
            session_pg.commit()
            print("Batch updated: ", [batch.code, batch.moodle_id])
        else:
            print("Batch {} not found".format(course.Curso_Id))
    except Exception as e:
        print(e)
        continue
