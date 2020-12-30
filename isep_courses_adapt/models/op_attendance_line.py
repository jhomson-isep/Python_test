# -*- coding: utf-8 -*-
from odoo import models, fields
from .op_mysql import MYSQL
import logging
import datetime

logger = logging.getLogger(__name__)

class OpAttendanceLine(models.Model):
    _inherit = 'op.attendance.line'

    justified = fields.Boolean(string="Justified", default=False)

    def set_register_id(self):
        logger.info("**************************************")
        logger.info("set register id in all atendances line")
        logger.info("**************************************")
        attendances = self.search([])
        for attendance in attendances:
            attendance.write({
                'register_id': attendance.attendance_id.register_id.id
            })
            logger.info("**************************************")
            logger.info("update line id %s" % attendance.id)
            logger.info("**************************************")
        logger.info("**************************************")
        logger.info("End of script")
        logger.info("**************************************")

    def import_all_attendances_moodle(self):
        self.get_attendance_register_mld()
        self.get_attendance_sheet_mdl()
        self.get_attendance_line_mdl()
        self.env['op.attendance.sheet'].set_name_attendance_sheet()

    def get_attendance_register_mld(self):
        mysql = MYSQL()
        attendances = mysql.get_all_attendance()
        for attendance in attendances:
            attendance_sessions = mysql.get_attendance_session_by_attendanceid(attendance['id'])
            for attendance_session in attendance_sessions:
                group = mysql.get_group_by_id(attendance_session['groupid'])
                if not group:
                    logger.info("**************************************")
                    logger.info("Group Not Exist Id: %s" % attendance_session['groupid'])
                    logger.info("**************************************")
                    continue
                attendance_reg = self.env['op.attendance.register'].\
                search([('code', '=', group[0]['name'])], limit=1)
                if len(attendance_reg) == 0:
                    batch = self.env['op.batch'].search([('code', '=', group[0]['name'])], limit=1)
                    if len(batch) == 0:
                        logger.info("**************************************")
                        logger.info("Batch Not Exist Code: %s" % group[0]['name'])
                        logger.info("**************************************")
                        continue
                    self.env['op.attendance.register'].create({
                        'name' : batch.code,
                        'code' : batch.code,
                        'batch_id' : batch.id,
                        'course_id' : batch.course_id.id,
                        'active' : True
                        })
                    logger.info("**************************************")
                    logger.info("Added attendance Register Code: %s" % (batch.code))
                    logger.info("**************************************")
                else:
                    logger.info("**************************************")
                    logger.info("Attendance Register Exist Code: %s" % batch.code)
                    logger.info("**************************************")
                    continue

    def get_attendance_sheet_mdl(self):
        mysql = MYSQL()
        attendances = mysql.get_all_attendance()
        for attendance in attendances:
            attendance_sessions = mysql.get_attendance_session_by_attendanceid(attendance['id'])
            for attendance_session in attendance_sessions:
                group = mysql.get_group_by_id(attendance_session['groupid'])
                if not group:
                    logger.info("**************************************")
                    logger.info("Group Not Exist Id: %s" % attendance_session['groupid'])
                    logger.info("**************************************")
                    continue
                attendance_reg = self.env['op.attendance.register'].\
                search([('code', '=', group[0]['name'])], limit=1)
                if len(attendance_reg) == 0:
                    logger.info("**************************************")
                    logger.info("Attendance Register Not Exist Code: %s" % group[0]['name'])
                    logger.info("**************************************")
                    continue
                attendance_sheet = self.env['op.attendance.sheet'].\
                search([('register_id', '=', attendance_reg.id),
                        ('attendance_date', '=', datetime.date.\
                        fromtimestamp(attendance_session.sessdate))], limit=1)
                if len(attendance_sheet) == 0:
                    self.env['op.attendance.sheet'].create({
                        'register_id' : attendance_reg.id,
                        'attendance_date' : datetime.date.\
                                            fromtimestamp(attendance_session.sessdate),
                        'active' : True,
                        'state' : 'draft'
                        })
                    logger.info("**************************************")
                    logger.info("Added attendance sheet")
                    logger.info("**************************************")
                else:
                    logger.info("**************************************")
                    logger.info("Attendance Sheet Exist Id %s" % attendance_sheet.id)
                    logger.info("**************************************")
                    continue

    def get_attendance_line_mdl(self):
        mysql = MYSQL()
        attendance_logs = mysql.get_all_attendance_log()
        for attendance_log in attendance_logs:
            session = mysql.get_attendance_session_by_id(attendance_log['sessionid'])
            if not session:
                logger.info("**************************************")
                logger.info("Attendance Session Not Exist ID: %s" % attendance_log['sessionid'])
                logger.info("**************************************")
                continue
            group = mysql.get_group_by_id(session[0]['groupid'])
            if not group:
                logger.info("**************************************")
                logger.info("Group Not Exist ID: %s" % session[0]['groupid'])
                logger.info("**************************************")
                continue
            status = mysql.get_attendance_status_by_id(attendance_log['statusid'])
            if not status:
                logger.info("**************************************")
                logger.info("Status Not Exist ID: %s" % attendance_log['statusid'])
                logger.info("**************************************")
                continue
            user = mysql.get_user_by_id(attendance_log['studentid'])
            if not user:
                logger.info("**************************************")
                logger.info("User Not Exist ID: %s" % attendance_log['studentid'])
                logger.info("**************************************")
                continue
            attendance_reg = self.env['op.attendance.register'].\
                search([('code', '=', group[0]['name'])], limit=1)
            if len(attendance_reg) == 0:
                logger.info("**************************************")
                logger.info("Attendance Register Not Exist Code: %s" % group[0]['name'])
                logger.info("**************************************")
                continue
            attendance_sheet = self.env['op.attendance.sheet'].\
            search([('register_id', '=', attendance_reg.id),
                    ('attendance_date', '=', datetime.date.\
                    fromtimestamp(attendance_session.sessdate))], limit=1)
            if len(attendance_sheet) == 0:
                logger.info("**************************************")
                logger.info("Attendance Sheet Not Exist Date: %s" % datetime.date.\
                            fromtimestamp(attendance_session.sessdate))
                logger.info("**************************************")
                continue
            op_student = self.env['op.student'].\
            search([('document_number', '=', user[0]['idnumber'])], limit=1)
            if len(op_student) == 0:
                logger.info("**************************************")
                logger.info("Student Not Exist Document Number: %s" % user[0]['idnumber'])
                logger.info("**************************************")
                continue
            attendance_line = self.env['op.attendance.line'].\
            search([('attendance_id', '=', attendance_sheet.id),
                    ('attendance_date', '=', attendance_sheet.attendance_date),
                    ('student_id', '=', op_student.id)], limit=1)
            if len(attendance_line) == 0:
                if status[0]['description'] is not '':
                    if status[0]['description'].upper() == 'PRESENTE' or status[0]['description'].upper() == 'RETRASO':
                        present = True
                        justified = False
                    elif status[0]['description'].upper() == 'FALTA INJUSTIFICADA':
                        present = False
                        justified = False
                    elif status[0]['description'].upper() == 'FALTA JUSTIFICADA':
                        present = False
                        justified = True
                else:
                    continue
                self.env['op.attendance.line'].create({
                    'attendance_id' : attendance_sheet.id,
                    'course_id' : attendance_reg.course_id.id,
                    'batch_id' : attendance_reg.batch_id.id,
                    'attendance_date' : attendance_sheet.attendance_date,
                    'active' : True,
                    'student_id' : op_student.id,
                    'register_id' : attendance_reg.id,
                    'present' : present if present else False,
                    'justified' : justified if justified else False 
                    })
                logger.info("**************************************")
                logger.info("Added Attendance Line" )
                logger.info("**************************************")
            else:
                logger.warning("**************************************")
                logger.warning("Attendance Line Exist Id: %s" % attendance_line.id)
                logger.warning("**************************************")
                continue
