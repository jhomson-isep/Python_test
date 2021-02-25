# -*- coding: utf-8 -*-
from dotenv import load_dotenv, find_dotenv
from mysql.connector import errorcode
import mysql.connector
import datetime
import logging
import os

logger = logging.getLogger(__name__)
load_dotenv(find_dotenv())
production = False


class MYSQL():
    config = {
        'user': 'odoo',
        'password': 'Iseplatam2020',
        'host': '192.168.0.153',
        'database': 'moodle'
    }

    if production:
        config = {
            'user': os.environ['MYSQL_USER'],
            'password': os.environ['MYSQL_PASSWORD'],
            'host': os.environ['MYSQL_HOST'],
            'database': os.environ['MYSQL_DATABASE']
        }

    def query(self, sql):
        logger.info(sql)
        try:
            cnx = mysql.connector.connect(**self.config)
            cursor = cnx.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            rows = []
        else:
            cnx.close()
        return rows

    def query_with_headers(self, sql):
        logger.info(sql)
        try:
            cnx = mysql.connector.connect(**self.config)
            cursor = cnx.cursor()
            cursor.execute(sql)
            columns = cursor.description
            rows = [{columns[index][0]: column for index, column in
                     enumerate(value)} for value in cursor.fetchall()]
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logger.info("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logger.info("Database does not exist")
            else:
                logger.info(err)
            rows = []
        else:
            cnx.close()
        return rows

    def query_get_one(self, sql):
        logger.info(sql)
        try:
            cnx = mysql.connector.connect(**self.config)
            cursor = cnx.cursor()
            cursor.execute(sql)
            rows = cursor.fetchone()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            rows = []
        else:
            cnx.close()
        return rows

    def query_recent_access(self, days=1):
        try:
            today = datetime.datetime.now()
            yesterday = today - datetime.timedelta(days=days)
            today = today.strftime('%Y-%m-%d')
            yesterday = yesterday.strftime('%Y-%m-%d')
            s = "\'"
            today = s + today + s
            yesterday = s + yesterday + s
            sql = ("""
                    SELECT
                    id,
                    idnumber,
                    username,
                    email,
                    lastaccess
                    FROM
                    mdl_user user
                    WHERE 
                    DATE(FROM_UNIXTIME(lastaccess, '%y/%m/%d %h:%i:%s')) 
                    BETWEEN {0} AND {1}
                    ORDER BY
                   lastaccess
                   DESC
                   """.format(yesterday, today))
            cursor = self.query(sql)
            rows = []
            if cursor != []:
                for (id, idnumber, username, email, last_access) in cursor:
                    rows.append({'id': id, 'idnumber': idnumber,
                                 'lastaccess': last_access})
        except Exception as e:
            rows = []
        return rows

    def get_moodle_grades(self, days=1):
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=days)
        yesterday = yesterday.strftime('%Y-%m-%d')
        s = "\'"
        yesterday = s + yesterday + s
        return self.query_with_headers(
            """
            SELECT 
            mdl_grade_items.id,
            mdl_grade_grades.userid,
            mdl_user.idnumber,
            mdl_user.firstname,
            mdl_user.lastname,
            mdl_user.department,
            mdl_grade_items.courseid,
            mdl_grade_items.categoryid,
            mdl_grade_items.idnumber item_idnumber,
            mdl_course.fullname,
            mdl_course.idnumber course_idnumber,
            mdl_course.shortname,
            mdl_groups.name as mdl_groups_name,
            mdl_grade_grades.finalgrade,
            mdl_grade_grades.timemodified,
            mdl_grade_grades.timecreated,
            DATE(FROM_UNIXTIME(mdl_grade_grades.timemodified, '%y/%m/%d %h:%i:%s')) AS dt_created
            FROM mdl_grade_items 
            JOIN mdl_grade_grades ON mdl_grade_items.id = mdl_grade_grades.itemid
            JOIN mdl_course ON mdl_grade_items.courseid = mdl_course.id
            JOIN mdl_user ON mdl_grade_grades.userid = mdl_user.id
            INNER JOIN mdl_groups on mdl_groups.courseid = mdl_course.id
            INNER JOIN mdl_groups_members ON mdl_groups_members.groupid = mdl_groups.id and mdl_groups_members.userid = mdl_user.id
            WHERE     
                DATE(FROM_UNIXTIME(mdl_grade_grades.timemodified, '%y/%m/%d 
                %h:%i:%s')) BETWEEN '{0}' AND NOW()
                AND  
                mdl_grade_grades.finalgrade IS NOT NULL
            ORDER BY mdl_grade_grades.id DESC;
            """.format(yesterday)
        )

    def get_all_attendance(self):
        try:
            cnx = mysql.connector.connect(**self.config)
            cursor = cnx.cursor()
            query = ("""
                SELECT id, course, name FROM mdl_attendance
                """)
            cursor.execute(query)
            rows = []
            for (id, course, name) in cursor:
                rows.append(
                    {
                    'id': id,
                    'course': course,
                    'name': name
                    })
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            rows=[]
        else:
            cnx.close()
        return rows

    def get_attendance_session_by_attendanceid(self, attendanceid):
        try:
            cnx = mysql.connector.connect(**self.config)
            cursor = cnx.cursor()
            query = ("""
                SELECT id, attendanceid, groupid, sessdate FROM mdl_attendance_sessions where attendanceid=%d
                """ % attendanceid)
            cursor.execute(query)
            rows = []
            for (id, attendanceid, groupid, sessdate) in cursor:
                rows.append(
                    {
                    'id': id,
                    'attendanceid': attendanceid,
                    'groupid': groupid,
                    'sessdate': sessdate
                    })
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            rows=[]
        else:
            cnx.close()
        return rows

    def get_group_by_id(self, id):
        try:
            cnx = mysql.connector.connect(**self.config)
            cursor = cnx.cursor()
            query = ("""
                SELECT id, courseid, idnumber, name FROM mdl_groups where id=%d
                """ % id)
            cursor.execute(query)
            rows = []
            for (id, courseid, idnumber, name) in cursor:
                rows.append(
                    {
                    'id': id,
                    'courseid': courseid,
                    'idnumber': idnumber,
                    'name': name
                    })
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            rows=[]
        else:
            cnx.close()
        return rows

    def get_all_attendance_log(self):
        try:
            cnx = mysql.connector.connect(**self.config)
            cursor = cnx.cursor()
            query = ("""
                SELECT id, sessionid, studentid, statusid  FROM mdl_attendance_log
                """)
            cursor.execute(query)
            rows = []
            for (id, sessionid, studentid, statusid) in cursor:
                rows.append(
                    {
                    'id': id,
                    'sessionid': sessionid,
                    'studentid': studentid,
                    'statusid': statusid
                    })
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            rows=[]
        else:
            cnx.close()
        return rows

    def get_attendance_session_by_id(self, id):
        try:
            cnx = mysql.connector.connect(**self.config)
            cursor = cnx.cursor()
            query = ("""
                SELECT id, attendanceid, groupid, sessdate FROM mdl_attendance_sessions where id=%d
                """ % id)
            cursor.execute(query)
            rows = []
            for (id, attendanceid, groupid, sessdate) in cursor:
                rows.append(
                    {
                    'id': id,
                    'attendanceid': attendanceid,
                    'groupid': groupid,
                    'sessdate': sessdate
                    })
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            rows=[]
        else:
            cnx.close()
        return rows

    def get_attendance_status_by_id(self, id):
        try:
            cnx = mysql.connector.connect(**self.config)
            cursor = cnx.cursor()
            query = ("""
                SELECT id, attendanceid, description FROM mdl_attendance_statuses where id=%d
                """ % id)
            cursor.execute(query)
            rows = []
            for (id, attendanceid, description) in cursor:
                rows.append(
                    {
                    'id': id,
                    'attendanceid': attendanceid,
                    'description': description
                    })
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            rows=[]
        else:
            cnx.close()
        return rows

    def get_user_by_id(self, id):
        try:
            cnx = mysql.connector.connect(**self.config)
            cursor = cnx.cursor()
            query = ("""
                SELECT id, idnumber FROM mdl_user where id=%d
                """ % id)
            cursor.execute(query)
            rows = []
            for (id, idnumber) in cursor:
                rows.append(
                    {
                    'id': id,
                    'idnumber': idnumber
                    })
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            rows=[]
        else:
            cnx.close()
        return rows

