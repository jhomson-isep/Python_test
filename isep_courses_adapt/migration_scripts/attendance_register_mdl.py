from sqlachemy_conn import (get_pg_session, get_mysql_session, OpAttendanceRegister,
                            OpBatch, MdlAttendanceSession, MdlAttendance,
                            MdlGroups, OpAttendanceSheet, MdlAttendanceLog,
                            MdlUser, MdlAttendanceStatuses, OpAttendanceLine,
                            OpStudent)
from sqlalchemy import and_
import logging
import datetime

session_pg = get_pg_session()
session_mysql = get_mysql_session()

attendances = session_mysql.query(MdlAttendance).all()

logger = logging.getLogger(__name__)

def get_attendance_register_mld():
    for attendance in attendances:
        attendances_session = session_mysql.query(MdlAttendanceSession).\
            filter(MdlAttendanceSession.attendanceid == attendance.id)
        for attendance_session in attendances_session:
            group = session_mysql.query(MdlGroups).\
                filter(MdlGroups.id == attendance_session.groupid).first()
            if group is None:
                logger.warning("**************************************")
                logger.warning("Group Not Exist Id: %s" % attendance_session.groupid)
                logger.warning("**************************************")
                continue
            attendance_reg = session_pg.query(OpAttendanceRegister).\
                filter(OpAttendanceRegister.code == group.name).first()
            if attendance_reg is None:
                batch = session_pg.query(OpBatch).\
                    filter(OpBatch.code == group.name).first()
                if batch is None:
                    logger.warning("**************************************")
                    logger.warning("Batch Not Exist Id: %s" % group.name)
                    logger.warning("**************************************")
                    continue
                attendance_reg = OpAttendanceRegister()
                attendance_reg.batch_id = batch.id
                attendance_reg.course_id = batch.course_id
                attendance_reg.name = batch.code
                attendance_reg.code = batch.code
                attendance_reg.active = True
                session_pg.add(attendance_reg)
                session_pg.commit()
                logger.warning("**************************************")
                logger.warning("Added attendance Register Code: %s" % (attendance_reg.code))
                logger.warning("**************************************")
            else:
                logger.warning("**************************************")
                logger.warning("Attendance Register Exist Code: %s" % batch.code)
                logger.warning("**************************************")
                continue

def get_attendance_sheet_mdl():
    for attendance in attendances:
        attendances_session = session_mysql.query(MdlAttendanceSession). \
            filter(MdlAttendanceSession.attendanceid == attendance.id)
        for attendance_session in attendances_session:
            group = session_mysql.query(MdlGroups). \
                filter(MdlGroups.id == attendance_session.groupid).first()
            if group is None:
                logger.warning("**************************************")
                logger.warning("Group Not Exist Id: %s" % attendance_session.groupid)
                logger.warning("**************************************")
                continue
            attendance_reg = session_pg.query(OpAttendanceRegister).\
                filter(OpAttendanceRegister.code == group.name).first()
            if attendance_reg is None:
                logger.warning("**************************************")
                logger.warning("Attendance Register Not Exist Code: %s" % group.name)
                logger.warning("**************************************")
                continue
            attendance_sheet = session_pg.query(OpAttendanceSheet).\
                filter(and_(OpAttendanceSheet.register_id == attendance_reg.id,
                            OpAttendanceSheet.attendance_date == datetime.date.\
                            fromtimestamp(attendance_session.sessdate))).first()
            if attendance_sheet is None:
                attendance_sheet = OpAttendanceSheet()
                attendance_sheet.register_id = attendance_reg.id
                attendance_sheet.attendance_date = datetime.date.\
                            fromtimestamp(attendance_session.sessdate)
                attendance_sheet.active = True
                attendance_sheet.state = 'draft'
                session_pg.add(attendance_sheet)
                session_pg.commit()
                logger.warning("**************************************")
                logger.warning("Added attendance sheet id: %s" % attendance_sheet.id)
                logger.warning("**************************************")
            else:
                logger.warning("**************************************")
                logger.warning("Attendance Sheet Exist ID: %s" % attendance_sheet.id)
                logger.warning("**************************************")
                continue

def get_attendance_line_mdl():
    attendances_log = session_mysql.query(MdlAttendanceLog).all()
    for attendance_log in attendances_log:
        session = session_mysql.query(MdlAttendanceSession).\
            filter(MdlAttendanceSession.id == attendance_log.sessionid).first()
        if session is None:
            logger.warning("**************************************")
            logger.warning("Attendance Session Not Exist ID: %s" % attendance_log.sessionid)
            logger.warning("**************************************")
            continue
        group = session_mysql.query(MdlGroups). \
                filter(MdlGroups.id == session.groupid).first()
        if group is None:
            logger.warning("**************************************")
            logger.warning("Group Not Exist ID: %s" % session.groupid)
            logger.warning("**************************************")
            continue
        status = session_mysql.query(MdlAttendanceStatuses).\
            filter(MdlAttendanceStatuses.id == attendance_log.statusid).first()
        if status is None:
            logger.warning("**************************************")
            logger.warning("Status Not Exist ID: %s" % attendance_log.statusid)
            logger.warning("**************************************")
            continue
        user = session_mysql.query(MdlUser).\
            filter(MdlUser.id == attendance_log.studentid).first()
        if user is None:
            logger.warning("**************************************")
            logger.warning("User Not Exist ID: %s" % attendance_log.studentid)
            logger.warning("**************************************")
            continue
        attendance_reg = session_pg.query(OpAttendanceRegister).\
            filter(OpAttendanceRegister.code == group.name).first()
        if attendance_reg is None:
            logger.warning("**************************************")
            logger.warning("Attendance Register Not Exist Code: %s" % group.name)
            logger.warning("**************************************")
            continue
        attendance_sheet = session_pg.query(OpAttendanceSheet).\
            filter(and_(OpAttendanceSheet.register_id == attendance_reg.id,
                        OpAttendanceSheet.attendance_date == datetime.date. \
                        fromtimestamp(session.sessdate))).first()
        if attendance_sheet is None:
            logger.warning("**************************************")
            logger.warning("Attendance Sheet Not Exist Date: %s" % datetime.date. \
                        fromtimestamp(session.sessdate))
            logger.warning("**************************************")
            continue
        op_student = session_pg.query(OpStudent).\
            filter(OpStudent.document_number == user.idnumber).first()
        if op_student is None:
            logger.warning("**************************************")
            logger.warning("Student Not Exist document_number: %s" % user.idnumber)
            logger.warning("**************************************")
            continue
        attendance_line = session_pg.query(OpAttendanceLine).\
            filter(and_(OpAttendanceLine.attendance_id == attendance_sheet.id,
                        OpAttendanceLine.attendance_date == attendance_sheet.attendance_date,
                        OpAttendanceLine.student_id == op_student.id)).first()
        if attendance_line is None:
            attendance_line = OpAttendanceLine()
            attendance_line.attendance_id = attendance_sheet.id
            attendance_line.course_id = attendance_reg.course_id
            attendance_line.batch_id = attendance_reg.batch_id
            attendance_line.attendance_date = attendance_sheet.attendance_date
            attendance_line.active = True
            attendance_line.student_id = op_student.id
            attendance_line.register_id = attendance_reg.id
            if status.description is not None:
                if status.description.upper() == 'PRESENTE' or status.description.upper() == 'RETRASO':
                    attendance_line.present = True
                    attendance_line.justified = False
                elif status.description.upper() == 'FALTA INJUSTIFICADA':
                    attendance_line.present = False
                    attendance_line.justified = False
                elif status.description.upper() == 'FALTA JUSTIFICADA':
                    attendance_line.present = False
                    attendance_line.justified = True
            else:
                continue
            session_pg.add(attendance_line)
            session_pg.commit()
            logger.warning("**************************************")
            logger.warning("Added Attendance Line Id: %s" % attendance_line.id)
            logger.warning("**************************************")
        else:
            logger.warning("**************************************")
            logger.warning("Attendance Line Exist Id: %s" % attendance_line.id)
            logger.warning("**************************************")
            continue


get_attendance_register_mld()
get_attendance_sheet_mdl()
get_attendance_line_mdl()
