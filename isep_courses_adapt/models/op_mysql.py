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

