from sqlachemy_conn import get_pg_session, get_session_server_isep, OpAttendanceRegister, OpAttendanceSheet, Asistencias
from sqlalchemy import and_
import logging

session_pg = get_pg_session()
session_server = get_session_server_isep()

attendances_reg = session_pg.query(OpAttendanceRegister).all()

logger = logging.getLogger(__name__)

for attendance_reg in attendances_reg:
    attendances = session_server.query(Asistencias).\
        filter(Asistencias.Curso_Id == attendance_reg.code)
    if attendances is None:
        logger.warning("**************************************")
        logger.warning("Attendance Not Exist! Code %s" % attendance_reg.code)
        logger.warning("**************************************")
        continue
    for attendance in attendances:
        attendance_sheet = session_pg.query(OpAttendanceSheet).\
        filter(and_(OpAttendanceSheet.register_id == attendance_reg.id,
                   OpAttendanceSheet.attendance_date == attendance.FechaAsistencia.date())).first()
        if attendance_sheet is None:
            attendance_sheet = OpAttendanceSheet()
            attendance_sheet.register_id = attendance_reg.id
            attendance_sheet.attendance_date = attendance.FechaAsistencia.date()
            attendance_sheet.active = True
            attendance_sheet.state = 'draft'
            session_pg.add(attendance_sheet)
            session_pg.commit()
            logger.warning("**************************************")
            logger.warning("Added attendance sheet id: %s" % attendance_sheet.id)
            logger.warning("**************************************")
        else:
            logger.warning("**************************************")
            logger.warning("Attendance sheet already exist id: %s" % attendance_sheet.id)
            logger.warning("**************************************")
    else:
        logger.warning("**************************************")
        logger.warning("Attendances not found")
        logger.warning("**************************************")
else:
    logger.warning("**************************************")
    logger.warning("Attendance Register not found")
    logger.warning("**************************************")


