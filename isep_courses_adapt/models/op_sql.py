# -*- coding: utf-8 -*-
import logging
import pyodbc
import os

logger = logging.getLogger(__name__)


class SQL():
    dsn = 'egServer70source'
    server = '85.118.244.220'
    user = 'sa'
    password = 'Gr5p4mr3'
    database = 'ISEP'
    driver = 'SQL Server'  # for Windows
    if os.name == "posix":
        driver = 'ODBC Driver 17 for SQL Server'  # for linux

    def query(self, sql):
        # con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (self.dsn, self.user, self.password, self.database)
        con_string = 'DRIVER={%s};SERVER=%s;UID=%s;PWD=%s;DATABASE=%s;' % (self.driver,
                                                                           self.server, self.user, self.password,
                                                                           self.database)
        conn = pyodbc.connect(con_string)
        cursor_sql = conn.cursor()
        cursor_sql.execute(sql)
        row = cursor_sql.fetchall()
        return row

    def query_get_one(self, sql):
        # con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (self.dsn, self.user, self.password, self.database)
        con_string = 'DRIVER={%s};SERVER=%s;UID=%s;PWD=%s;DATABASE=%s;' % (self.driver,
                                                                           self.server, self.user, self.password,
                                                                           self.database)
        conn = pyodbc.connect(con_string)
        cursor_sql = conn.cursor()
        cursor_sql.execute(sql)
        row = cursor_sql.fetchone()
        return row

    def get_distinct_courses(self):
        # rows = self.query("SELECT DISTINCT SUBSTRING(Curso_id, 3, 2) FROM Cursos;")
        rows = self.query("SELECT DISTINCT SUBSTRING(Curso_id, 3, 2) FROM Cursos;")
        return rows

    def get_all_courses(self):
        rows = self.query(
            "SELECT *, SUBSTRING(Curso_Id, 3, 2) AS code FROM Cursos WHERE FechaAlta between '2018-01-01' and '2020-31-12';")
        return rows

    def get_course_by_code(self, code):
        row = self.query_get_one(
            "SELECT * FROM Cursos WHERE SUBSTRING(Curso_Id, 3,2)='{0}' ORDER BY id DESC;".format(code))
        return row

    def get_all_subjects(self):
        rows = self.query(
            "SELECT * FROM Asignaturas ORDER BY id DESC")
        return rows

    def get_subject_rel_by_code(self, subject_code):
        rows = self.query(
            "SELECT * FROM CursosAsignaturas WHERE CodAsignatura = '{0}';".format(subject_code))
        return rows
