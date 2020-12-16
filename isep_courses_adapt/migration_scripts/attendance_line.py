from sqlachemy_conn import get_pg_session, get_session_server_isep, OpCourse, OpStudent, OpFaculty, OpAttendanceRegister, OpAttendanceSheet, OpAttendanceLine, Asistencias, OpBatch
from sqlalchemy import and_
import logging

session_pg = get_pg_session()
session_server = get_session_server_isep()

attendances_reg = session_pg.query(OpAttendanceRegister).all()

logger = logging.getLogger(__name__)


