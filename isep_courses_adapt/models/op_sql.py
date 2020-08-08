# -*- coding: utf-8 -*-
import logging
import pyodbc

logger = logging.getLogger(__name__)


class SQL():
    dsn = 'egServer70source'
    server = '85.118.244.220'
    user = 'sa'
    password = 'Gr5p4mr3'
    database = 'ISEP'

    def Send_SQL(self):
        # con_string = 'DRIVER={SQL Server};DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (self.dsn, self.user, self.password, self.database)
        con_string = 'DRIVER={SQL Server};UID=%s;PWD=%s;DATABASE=%s;' % (
            self.user, self.password, self.database)
        # con_string = 'DSN=85.118.244.220;UID=sa;PWD=Gr5p4mr3;DATABASE=GrupoISEPxtra;'

        cnxn = pyodbc.connect(con_string)
        # cnxn = pyodbc.connect(server='85.118.244.220',UID='sa',PWD='Gr5p4mr3',DATABASE='GrupoISEPxtra')

        cursorsql = cnxn.cursor()
        cursorsql.execute("SELECT id,curso_id,NombreCurso from Cursos;")
        row = cursorsql.fetchone()
        while row:
            # print row[0]
            # print row[1]
            # print row[2]
            row = cursorsql.fetchone()

        cnxn.commit()

    def get_distinct_courses(self):
        rows = self.query("SELECT DISTINCT SUBSTRING(Curso_id, 3, 2) FROM Cursos;")
        return rows

    def get_course_by_code(self, code):
        rows = self.query(
            "SELECT TOP (1) * FROM Cursos WHERE SUBSTRING(Curso_Id, 3,2)='{0}' ORDER BY id DESC;".format(code))
        return rows

    def query(self, sql):
        # con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (self.dsn, self.user, self.password, self.database)
        con_string = 'DRIVER={SQL Server};SERVER=%s;UID=%s;PWD=%s;DATABASE=%s;' % (
            self.server, self.user, self.password, self.database)
        conn = pyodbc.connect(con_string)
        cursor_sql = conn.cursor()
        cursor_sql.execute(sql)
        row = cursor_sql.fetchall()
        return row
