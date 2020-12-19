from sqlachemy_conn import get_pg_session, get_session_server_isep, OpAttendanceRegister, Asistencias, OpBatch
from sqlalchemy import and_
import logging

session_pg = get_pg_session()
session_server = get_session_server_isep()

attendances = session_server.query(Asistencias).\
    filter(Asistencias.Marca != '')

logger = logging.getLogger(__name__)
for attendance in attendances:
    attendance_reg = session_pg.query(OpAttendanceRegister).\
                    filter(OpAttendanceRegister.code == attendance.Curso_Id).first()
    if attendance_reg is None:
        attendance_reg = OpAttendanceRegister()
        batch_id = session_pg.query(OpBatch). \
            filter(OpBatch.code == attendance.Curso_Id).first()
        if batch_id is None:
            logger.warning("**************************************")
            logger.warning("Batch Not Exist Code: %s" % attendance.Curso_Id)
            logger.warning("**************************************")
            continue
        attendance_reg.name = batch_id.code
        attendance_reg.code = attendance.Curso_Id
        attendance_reg.batch_id = batch_id.id
        attendance_reg.course_id = batch_id.course_id
        attendance_reg.active = True
        session_pg.add(attendance_reg)
        session_pg.commit()
        logger.warning("**************************************")
        logger.warning("Added attendance Register Code: %s" % (attendance_reg.code))
        logger.warning("**************************************")
    else:
        logger.warning("**************************************")
        logger.warning("Attendance already exist code: %s" % attendance_reg.code)
        logger.warning("**************************************")
else:
    logger.warning("**************************************")
    logger.warning("Attendances not found")
    logger.warning("**************************************")
