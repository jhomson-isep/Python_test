# -*- coding: utf-8 -*-
from dotenv import load_dotenv, find_dotenv
import psycopg2
import os

load_dotenv(find_dotenv())


class PSQL():
    dbname = os.environ['DATABASE']
    user = os.environ['PSQL_USER']
    password = os.environ['PSQL_PASSWORD']
    host = os.environ['HOST_IP']
    port = os.environ['PORT']

    conn = psycopg2.connect("dbname=%s user=%s password=%s host=%s port=%s"
                            % (dbname, user, password, host, port))
    cr = conn.cursor()

    def get_all_batch(self):
        self.cr.execute('SELECT * FROM op_batch;')
        return self.cr.fetchall()

    def get_batch_by_code(self, code):
        self.cr.execute("SELECT id FROM op_batch WHERE code = '%s';" % code)
        return self.cr.fetchone()

    def get_course_by_code(self, code):
        self.cr.execute("SELECT * FROM op_course WHERE code = '%s';" % code)
        return self.cr.fetchone()

    def get_partner_by_name(self, name):
        self.cr.execute("SELECT id FROM res_partner WHERE name = '%s';" % name)
        return self.cr.fetchone()

    def get_campus_by_name(self, name):
        self.cr.execute("SELECT id FROM op_campus WHERE name = '%s';" % name)
        return self.cr.fetchone()

    def get_campus_by_code(self, code):
        self.cr.execute("SELECT id FROM op_campus WHERE code = '%s';" % code)
        return self.cr.fetchone()

    def get_practices_type_by_name(self, name):
        self.cr.execute("SELECT id FROM op_practices_type WHERE name = '%s';" % name)
        return self.cr.fetchone()

    def get_country_by_name(self, name):
        self.cr.execute("SELECT id FROM res_country WHERE name = '%s';" % name)
        return self.cr.fetchone()

    def get_partner_by_email_or_name(self, email, name):
        self.cr.execute("SELECT id FROM res_partner WHERE name = '%s' or email = '%s';" % (name, email))
        return self.cr.fetchone()

    def get_document_type_by_code(self, code):
        self.cr.execute("SELECT id FROM op_document_type WHERE code = '%s';" % code)
        return self.cr.fetchone()

    def get_study_type_by_code(self, code):
        self.cr.execute("SELECT id FROM op_study_type WHERE code = '%s';" % code)
        return self.cr.fetchone()

    def get_university_by_code(self, code):
        self.cr.execute("SELECT id FROM op_university WHERE code = '%s';" % code)
        return self.cr.fetchone()

    def get_all_students(self):
        self.cr.execute("SELECT * FROM op_student;")
        return self.cr.fetchall()

    def get_sutdent_by_gr_no(self, gr_no):
        self.cr.execute("SELECT id FROM op_student "
                        "WHERE gr_no = '%s';" % gr_no)
        return self.cr.fetchone()

    def get_get_all_faculties(self):
        self.cr.execute("SELECT * FROM op_faculty;")
        return self.cr.fetchall()

    def get_faculty_by_nifp(self, nifp):
        self.cr.execute("SELECT id FROM op_faculty"
                        " WHERE nifp = '%s';" % nifp)
        return self.cr.fetchone()

    def get_partner_by_vat(self, vat):
        self.cr.execute("SELECT id FROM res_partner "
                        "WHERE vat = '%s';" % vat)
        return self.cr.fetchone()

    def get_partner_by_email(self, email):
        self.cr.execute("SELECT id FROM res_partner "
                        "WHERE vat = '%s';" % email)
        return self.cr.fetchone()

    def create_partner(self, values):
        self.cr.execute("INSERT INTO res_partner "
                        "(display_name, name, email, phone, mobile, street,"
                        "zip, city, country_id, vat, is_student, active) VALUES ('%s','%s', '%s', '%s', '%s',"
                        " '%s', '%s', '%s', %s, '%s', %s, TRUE);" % (values[0], values[0], values[1], values[2],
                                                                     values[3], values[4], values[5],
                                                                     values[6], values[7], values[8],
                                                                     values[9])
                        )
        self.conn.commit()

    def create_faculty(self, values):
        self.cr.execute("INSERT INTO op_faculty "
                        "(first_name, last_name, "
                        "birth_date, gender, nationality, partner_id,"
                        " nifp, active) VALUES ( '%s', '%s', '%s', '%s', %s, %s, '%s', TRUE);" %
                        (values[0], values[1], values[2], values[3], values[4], values[5], values[6])
                        )
        self.conn.commit()

    def create_student(self, values):
        self.cr.execute("INSERT INTO op_student "
                        "(first_name, last_name, "
                        "partner_id, birth_date, gender, nationality, "
                        "n_id, gr_no, campus_id, curp, year_end_studies, "
                        "document_type_id, document_number, study_type_id, university_id, "
                        "moodle_id, moodle_user, active) VALUES ('%s', '%s', %s, '%s', "
                        "'%s', %s, '%s', '%s', %s,'%s', %s, %s, '%s', %s, %s, %s, '%s', TRUE);" % (
                            values[0], values[1], values[2],
                            values[3], values[4], values[5],
                            values[6], values[7], values[8],
                            values[9], values[10], values[11],
                            values[12], values[13], values[14],
                            values[15], values[16]))
        self.conn.commit()

    def create_batch(self, values):
        self.cr.execute("INSERT INTO op_batch "
                        "(name, code, course_id, start_date,"
                        " end_date, coordinator, campus_id, date_diplomas,"
                        " academic_year, days_week, schedule, class_place, "
                        "students_limit, type_practices, active) "
                        "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', {5}, {6}, '{7}', '{8}',"
                        " '{9}', '{10}', '{11}', "
                        "'{12}', {13}, TRUE);".format(values[0], values[1], values[2], values[3], values[4],
                                                      values[5], values[6], values[7], values[8], values[9],
                                                      values[10], values[11], values[12], values[13])
                        )
        self.conn.commit()

    def create_record(self, table, records):
        marks = ', '.join('?' * len(records))
        query = "INSERT INTO %s (%s) VALUES (%s);" % (table, marks, marks)
        self.cr.execute(query, marks.keys() + marks.values())
        self.cr.commit()
