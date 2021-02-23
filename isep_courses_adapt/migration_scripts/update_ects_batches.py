# -*- coding: utf-8 -*-

from sqlalchemy import and_, desc, or_
from sqlachemy_conn import *
import traceback


session_pg = get_pg_session()
session_sql = get_session_server_isep()

courses = session_sql.query(IsepCursos).all()

for course in courses:
    try:
        course_code = course.Curso_Id[2:4]
        op_courses = session_pg.query(OpCourse).filter(
            OpCourse.code == course_code).all()

        for op_course in op_courses:
            # print("ects: ", [op_course.ects, course.ECTS])
            # print("hours: ", [op_course.hours, course.TotalHoras])
            # print("credits: ", [op_course.credits, course.TotalCreditos])
            update = False
            if course.ECTS is not None or course.ECTS != 0:
                op_course.ects = int(course.ECTS)
                update = True
            if course.TotalHoras is not None:
                op_course.hours = float(course.TotalHoras)
                update = True
            if course.TotalCreditos is not None:
                op_course.credits = float(course.TotalCreditos)
                update = True
            if update:
                session_pg.commit()
                print("Course updated: ", [op_course.code, op_course.ects])
            else:
                print("No course data for updated: ",
                      [op_course.code, op_course.ects])
    except Exception as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        continue
