from sqlachemy_conn import get_pg_session, get_session_server_isep, OpCourse, OpStudent, OpFaculty, OpAttendanceRegister, OpAttendanceSheet, OpAttendanceLine, Asistencias, OpBatch
from sqlalchemy import and_
import logging

session_pg = get_pg_session()
session_server = get_session_server_isep()

attendances_sheet = session_pg.query(OpAttendanceSheet).all()

logger = logging.getLogger(__name__)

for attendance_sheet in attendances_sheet:
    attendance_reg = session_pg.query(OpAttendanceRegister).\
        filter(OpAttendanceRegister.id == attendance_sheet.register_id)
    attendances = session_server.query(Asistencias).\
        filter(and_(Asistencias.FechaAlta == attendance_sheet.attendance_date,
                    Asistencias.Curso_Id == attendance_reg.code))
    for attendance in attendances:
        student = session_pg.query(OpStudent).filter(OpStudent.gn_ro == attendance.N_Id).first()
        attendance_line = session_pg.query(OpAttendanceLine).\
            filter(and_(OpAttendanceLine.attendance_id == attendance_sheet.id,
                        OpAttendanceLine.attendance_date == attendance_sheet.attendance_date,
                        OpAttendanceLine.student_id == student.id)).first()
        if attendance_line is None:
            attendance_line = OpAttendanceLine()
            attendance_line.attendance_id = attendance_sheet.id
            attendance_line.course_id = attendance_reg.course_id
            attendance_line.batch_id = attendance_reg.batch_id
            attendance_line.attendance_date = attendance_sheet.attendance_date
            attendance_line.active = True
            attendance_line.student_id = student.id
            session_pg.add(attendance_line)
            session_pg.commit()
            logger.info("**************************************")
            logger.info("Added attendance line id: %s" % (attendance_line.id))
            logger.info("**************************************")
            print("Added attendance line id: %s" % (attendance_line.id))
        else:
            logger.warning("**************************************")
            logger.warning("Attendance already exist id: %s" % attendance_line.id)
            logger.warning("**************************************")
            print("Attendance already exist code: %s" % attendance_line.id)
    else:
        logger.warning("**************************************")
        logger.warning("Attendances not found")
        logger.warning("**************************************")
        print("Attendances not found")




