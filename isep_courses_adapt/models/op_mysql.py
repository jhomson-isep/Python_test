import logging
import datetime
import mysql.connector
from mysql.connector import errorcode

logger = logging.getLogger(__name__)

class MYSQL():
    config = {
        'user': 'odoo',
        'password': 'Iseplatam2020',
        'host': '192.168.0.153',
        'database': 'moodle'
    }

    def query(self, days=1):
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=days)
        today = today.strftime('%Y-%m-%d')
        yesterday = yesterday.strftime('%Y-%m-%d')
        try:
            cnx = mysql.connector.connect(**self.config)
            cursor = cnx.cursor()
            s = "\'"
            today = s + today + s
            yesterday = s + yesterday + s
            query = ("""
                SELECT
                id,
                idnumber,
                username,
                email,
                lastaccess
                FROM
                mdl_user user
                WHERE
                DATE(FROM_UNIXTIME(lastaccess, '%y/%m/%d %h:%i:%s')) BETWEEN """ +
                     yesterday +
                     """ AND """ +
                     today +
                     """
                      ORDER BY
                     lastaccess
                     DESC
                     """)
            cursor.execute(query)
            rows = []
            for (id, idnumber, username, email, lastaccess) in cursor:
                if 'idnumber' != '':
                    #logger.info({'id': id, 'idnumber': idnumber, 'lastaccess': lastaccess})
                    rows.append({'id': id, 'idnumber': idnumber, 'lastaccess': lastaccess})
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

