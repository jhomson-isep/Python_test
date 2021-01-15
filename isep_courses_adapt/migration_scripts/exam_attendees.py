from sqlalchemy import and_, desc
from datetime import datetime
from sqlachemy_conn import *
import traceback

# SQL SERVER SESSION
session_server = get_session_server_isep()
# SQL SERVER AREAS
scores = session_server.query(Calificaciones).order_by(desc(
    Calificaciones.FechaAlta)).all()
# POSTGRES SERVER SESSION
session_pg = get_pg_session()

for score in scores:
    try:
        session_code = score.Curso_Id + score.CodAsignatura
        exam = session_pg.query(OpExam).filter(
            OpExam.exam_code == session_code).first()
        student = session_pg.query(OpStudent).filter(
            OpStudent.n_id == str(score.N_Id)).first()

        if student is not None and exam is not None:
            attendee = session_pg.query(OpExamAttendees).filter(and_(
                OpExamAttendees.student_id == student.id,
                OpExamAttendees.exam_id == exam.id)).first()
            try:
                marks = float(score.NotaJunio)
            except Exception as ex:
                print(ex)
                marks = 0

            if attendee is None:
                attendee = OpExamAttendees()
                attendee.exam_id = exam.id
                attendee.student_id = student.id
                attendee.batch_id = exam.batch_id
                attendee.course_id = exam.course_id
                attendee.marks = marks
                attendee.order = score.Orden
                attendee.course_type = score.Curso_Tipo
                attendee.original_marks = score.NotaJunio
                attendee.note = score.Observaciones
                attendee.modify = score.Modifica
                attendee.status = 'present'
                attendee.is_final = True
                session_pg.add(attendee)
                session_pg.commit()
                print("Attendee created: ", [attendee.id, score.N_Id])
            else:
                print("Attendee already exist: ", [attendee.id, score.N_Id])
        else:
            not_found = "Exam" if exam is None else "Student"
            print("{} not found: {}".format(not_found, session_code))
    except Exception as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        continue
print("Migration terminated")
