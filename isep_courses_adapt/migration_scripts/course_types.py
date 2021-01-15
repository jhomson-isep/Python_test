from sqlalchemy import and_, desc
from sqlachemy_conn import *
from moodle import *

session_pg = get_pg_session()
session_sql = get_session_server()
Moodle = MoodleLib()

cursos_tipo = session_sql.query(GinTipoCurso).filter(and_(
    GinTipoCurso.Codigo != 'False', GinTipoCurso.Nombre != 'False',
    GinTipoCurso.Codigo != '-', GinTipoCurso.Codigo != 'n/a')).all()

for curso_tipo in cursos_tipo:
    try:
        print(curso_tipo.Codigo)
        course_type = session_pg.query(OpCourseType).filter(
            OpCourseType.code == curso_tipo.Codigo).first()
        if course_type is None:
            course_type = OpCourseType()
            course_type.name = curso_tipo.Nombre
            course_type.code = curso_tipo.Codigo
            session_pg.add(course_type)
            session_pg.commit()
            print("Course type created: ", course_type.code)
        else:
            print("Course type already exist: {}".format(curso_tipo.Codigo))
    except Exception as e:
        print(e)
        continue
