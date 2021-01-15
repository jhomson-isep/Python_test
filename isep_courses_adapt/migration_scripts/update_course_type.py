from sqlachemy_conn import *

session_pg = get_pg_session()
session_sql = get_session_server()

gin_courses = session_sql.query(GinCurso, GinTipoCurso).join(
    GinTipoCurso, GinCurso.TipoCursoID == GinTipoCurso.ID).all()

for gin_course in gin_courses:
    try:
        courses = session_pg.query(OpCourse).filter(
            OpCourse.code == gin_course.GinCurso.Codigo).all()
        course_type = session_pg.query(OpCourseType).filter(
            OpCourseType.code == gin_course.GinTipoCurso.Codigo).first()
        for course in courses:
            if course_type is not None:
                course.course_type_id = course_type.id
                session_pg.commit()
                print("Course updated: ", course.name)
            else:
                print("Course type not exist: ",
                      gin_course.GinTipoCurso.Codigo)
    except Exception as e:
        print(e)
        continue
