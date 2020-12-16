from sqlachemy_conn import get_pg_session, get_session_server_isep, OpAttendanceRegister, OpAttendanceSheet, Asistencias
from sqlalchemy import and_
import logging

session_pg = get_pg_session()
session_server = get_session_server_isep()

attendances_reg = session_pg.query(OpAttendanceRegister).all()

logger = logging.getLogger(__name__)

for attendance_reg in attendances_reg:
    attendances = session_pg.query(Asistencias).\
        where(Asistencias.Curso_Id == attendance_reg.code)
    for attendance in attendances:
        attendance_sheet = session_pg.query(OpAttendanceSheet).\
        where(and_(OpAttendanceSheet.register_id == attendance_reg.id,
                   OpAttendanceSheet.attendance_date == attendance.FechaAlta))
        if attendance_sheet is None:
            attendance_sheet = OpAttendanceSheet()
            attendance_sheet.register_id = attendance_reg.id
            attendance_sheet.attendance_date = attendance.FechaAlta.date()
            attendance_sheet.active = True
            session_pg.add(attendance_sheet)
            session_pg.commit()
            logger.info("**************************************")
            logger.info("Added attendance Register id: %s" % (attendance_sheet.id))
            logger.info("**************************************")
            print("Added attendance Register Code: %s" % (attendance_sheet.id))
        else:
            logger.warning("**************************************")
            logger.warning("Attendance already exist id: %s" % attendance_sheet.id)
            logger.warning("**************************************")
            print("Attendance already exist code: %s" % attendance_sheet.id)


