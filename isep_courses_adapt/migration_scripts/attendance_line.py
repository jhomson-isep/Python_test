from sqlachemy_conn import get_pg_session, get_session_server_isep, OpCourse, OpStudent, OpFaculty, OpAttendanceRegister, OpAttendanceSheet, OpAttendanceLine, Asistencias, OpBatch
from sqlalchemy import and_
import logging
import datetime

session_pg = get_pg_session()
session_server = get_session_server_isep()

attendances = session_server.query(Asistencias).all()

logger = logging.getLogger(__name__)

for attendance in attendances:
    attendance_reg = session_pg.query(OpAttendanceRegister).\
        filter(OpAttendanceRegister.code == attendance.Curso_Id).first()
    if attendance_reg is None:
        logger.warning("**************************************")
        logger.warning("Attendance Register Not Exist! Code %s" % attendance.Curso_Id)
        logger.warning("**************************************")
        continue
    attendance_sheet = session_pg.query(OpAttendanceSheet). \
        filter(and_(OpAttendanceSheet.register_id == attendance_reg.id,
                    OpAttendanceSheet.attendance_date == attendance.FechaAsistencia.date())).first()
    if attendance_sheet is None:
        logger.warning("**************************************")
        logger.warning("Attendance Sheet Not Exist! Code %s" % attendance_reg.id)
        logger.warning("**************************************")
        continue
    student = session_pg.query(OpStudent). \
        filter(OpStudent.gr_no == str(attendance.N_Id)).first()
    if student is None:
        logger.warning("**************************************")
        logger.warning("Student Not Exist! gr_no: %s" % attendance.N_Id)
        logger.warning("**************************************")
        continue
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
        if attendance.Marca is not None:
            if attendance.Marca.upper() == 'A':
                attendance_line.present = True
                attendance_line.justified = False
            elif attendance.Marca.upper() == 'FALTA':
                attendance_line.present = False
                attendance_line.justified = False
            elif attendance.Marca.upper() == 'JUSTIFICADA':
                attendance_line.present = False
                attendance_line.justified = True
        else:
            continue
        session_pg.add(attendance_line)
        session_pg.commit()
        logger.warning("**************************************")
        logger.warning("Added attendance line id: %s" % (attendance_line.id))
        logger.warning("**************************************")
    else:
        logger.warning("**************************************")
        logger.warning("Attendance line already exist id: %s" % attendance_line.id)
        logger.warning("**************************************")
else:
    logger.warning("**************************************")
    logger.warning("Attendances not found")
    logger.warning("**************************************")
