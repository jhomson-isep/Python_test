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
        # con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (self.dsn,
        # self.user, self.password, self.database)
        logger.info(sql)
        con_string = 'DRIVER={' \
                     '%s};SERVER=%s;UID=%s;PWD=%s;DATABASE=%s;PORT=1433;' % (
                         self.driver, self.server, self.user, self.password,
                         self.database)
        conn = pyodbc.connect(con_string)
        cursor_sql = conn.cursor()
        cursor_sql.execute(sql)
        row = cursor_sql.fetchall()
        return row

    def query_get_one(self, sql):
        # con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (self.dsn,
        # self.user, self.password, self.database)
        # logger.info(sql)
        con_string = 'DRIVER={' \
                     '%s};SERVER=%s;UID=%s;PWD=%s;DATABASE=%s;PORT=1433;' % (
                         self.driver, self.server, self.user, self.password,
                         self.database)
        conn = pyodbc.connect(con_string)
        cursor_sql = conn.cursor()
        cursor_sql.execute(sql)
        row = cursor_sql.fetchone()
        return row

    def get_distinct_courses(self):
        rows = self.query("SELECT DISTINCT SUBSTRING(Curso_id, 3, 2) FROM "
                          "Cursos;")
        return rows

    def get_all_courses(self, offset):
        rows = self.query(
            "SELECT *, SUBSTRING(Curso_Id, 3, 2) AS code FROM Cursos ORDER "
            "BY Id DESC OFFSET ({0}) ROWS FETCH NEXT 1000 ROWS "
            "ONLY;".format(offset))
        return rows

    def get_course_by_code(self, code):
        row = self.query_get_one(
            "SELECT * FROM Cursos WHERE SUBSTRING(Curso_Id, 3,2)='{0}' "
            "ORDER BY id DESC;".format(code))
        return row

    def get_all_subjects(self):
        rows = self.query(
            "SELECT * FROM Asignaturas ORDER BY id DESC")
        return rows

    def get_all_subject_rel(self):
        return self.query("SELECT * FROM CursosAsignaturas;")

    def get_subject_rel_by_code(self, subject_code):
        return self.query(
            "SELECT * FROM CursosAsignaturas WHERE CodAsignatura "
            "= '{0}';".format(subject_code))

    def get_all_students(self):
        return self.query(
            "SELECT * FROM Alumnos ORDER BY N_Id DESC;")

    def get_filtered_students(self):
        return self.query(
            "SELECT * FROM Alumnos WHERE N_Id NOT IN (SELECT "
            "DISTINCT al.N_Id FROM Alumnos al LEFT JOIN "
            "GrupoISEPxtra.dbo.gin_PreMatriculas pm ON al.N_Id = pm.AlumnoID "
            "WHERE pm.AnyAcademico IS NOT NULL AND pm.SedeID in (7,8,9,10,"
            "11,12,13,27) AND pm.Tramitada = 1 ) ORDER BY N_Id DESC;")

    def get_province_by_nid(self, nid):
        row = self.query_get_one(
            "SELECT tbl.NomItem AS provincia , al.NombreEmpresa AS "
            "nombre_empresa, al.DireccionEmpresa, al.TelefonoEmpresa, "
            "al.PoblacionEmpresa, al.CodPostalEmpresa, al.CodPostalEmpresa "
            "FROM Alumnos al JOIN Tablas tbl ON al.ProvinciaEmpresa = "
            "tbl.CodItem AND tbl.CodTaula = 'PR' WHERE al.NombreEmpresa IS "
            "NOT NULL AND al.N_Id = {0};".format(nid))
        return row

    def get_country_by_nid(self, nid):
        row = self.query_get_one(
            "SELECT tbl.NomItem AS country FROM Alumnos al JOIN Tablas tbl "
            "ON al.Pais = tbl.CodItem AND tbl.CodTaula = 'PA' WHERE al.Pais "
            "IS NOT NULL AND al.N_Id = {0};".format(nid))
        return row

    def get_all_faculties(self, offset):
        rows = self.query(
            "SELECT * FROM Profesores ORDER BY Id DESC OFFSET ({0}) ROWS "
            "FETCH NEXT 1000 ROWS ONLY;".format(offset))
        return rows

    def get_country_by_nifp(self, nifp):
        row = self.query_get_one(
            "SELECT tbl.NomItem AS country FROM Profesores al JOIN Tablas tbl "
            "ON al.Pais = tbl.CodItem AND tbl.CodTaula = 'PA' WHERE al.Pais "
            "IS NOT NULL AND al.NIFP = '{0}';".format(nifp))
        return row

    def get_all_batch(self, offset):
        rows = self.query(
            "SELECT Alumnos.N_Id AS gr_no, SUBSTRING(Matriculaciones.Curso_Id, 3, 2) AS code, Matriculaciones.Curso_Id As batch "
            "FROM Alumnos,  Matriculaciones WHERE Alumnos.N_Id = Matriculaciones.N_Id "
            "AND Alumnos.N_Id NOT IN "
            "(SELECT DISTINCT al.N_Id FROM ISEP.dbo.Alumnos al "
            "LEFT JOIN  GrupoISEPxtra.dbo.gin_PreMatriculas pm ON al.N_Id = pm.AlumnoID "
            "WHERE pm.AnyAcademico IS NOT NULL AND pm.SedeID in (7,8,9,10,11,12,13,27) AND pm.Tramitada = 1 ) "
            "ORDER BY Alumnos.N_Id DESC;"
        )
        return rows

    def get_all_batch_subject(self, offset):
        rows = self.query(
            "SELECT *, SUBSTRING(Curso_Id, 3, 2) AS code FROM CursosAsignaturas "
            "ORDER BY N_Id DESC OFFSET ({0}) ROWS FETCH NEXT 1000 ROWS ONLY;".format(offset)
        )
        return rows

    def get_all_subjects_by_course_student(self, course, gr_no):
        return self.query(
            "SELECT TOP(1000) Asignaturas.Id, Asignaturas.CodAsignatura, "
            "AL.N_Id, MA.Curso_Id, AL.Nombre FROM Asignaturas INNER JOIN "
            "CursosAsignaturas CA ON CA.CodAsignatura = "
            "Asignaturas.CodAsignatura INNER JOIN Matriculaciones MA ON "
            "MA.Curso_Id = '%s' AND CA.Curso_Id = '%s' INNER JOIN Alumnos AL "
            "ON AL.N_Id = '%s' AND MA.N_Id = '%s' AND AL.N_Id NOT IN (SELECT "
            "DISTINCT al.N_Id FROM ISEP.dbo.Alumnos al LEFT JOIN "
            "GrupoISEPxtra.dbo.gin_PreMatriculas pm ON al.N_Id = pm.AlumnoID "
            "WHERE pm.AnyAcademico IS NOT NULL AND pm.SedeID in "
            "(7,8,9,10, 11,12,13,27) AND pm.Tramitada = 1 ) ORDER BY "
            "Asignaturas.Id DESC;" % (course, course, gr_no, gr_no)
        )

    def get_all_subjects_faculty(self, faculty):
        rows = self.query(
            "SELECT CursosAsignaturas.NIF_Profesor, CursosAsignaturas.CodAsignatura "
            "FROM ISEP.dbo.CursosAsignaturas WHERE "
            "CursosAsignaturas.NIF_Profesor = '{0}';".format(faculty)
        )
        return rows

    def get_all_history(self):
        rows = self.query(
            "SELECT N_Id, Fecha, Observaciones, Usuario "
            "FROM ISEP.dbo.Historico;"
            )
        return rows
