import psycopg2
dbname = 'ISEP'
user = 'openpg'
password = 'openpgpwd'
host = 'localhost'
port = '5432'

class PSQL():
    conn = psycopg2.connect("dbname=%s user=%s password=%s host=%s port=%s" % (dbname, user, password, host, port))
    cr = conn.cursor()


    def get_all_batch(self):
        self.cr.execute('SELECT * FROM op_batch;')
        return self.cr.fetchall()

    def get_batch_by_code(self, code):
        self.cr.execute("SELECT id FROM op_batch WHERE code = '%s';" % (code))
        return self.cr.fetchone()

    def get_course_by_code(self, code):
        self.cr.execute("SELECT * FROM op_course WHERE code = '%s';" % (code))
        return self.cr.fetchone()

    def get_partner_by_name(self, name):
        self.cr.execute("SELECT id FROM res_partner WHERE name LIKE '%s';" % (name))
        return self.cr.fetchone()

    def get_campus_by_name(self, name):
        self.cr.execute("SELECT id FROM op_campus WHERE name LIKE '%s';" % (name))
        return self.cr.fetchone()

    def get_practices_type_by_name(self, name):
        self.cr.execute("SELECT id FROM op_practices_type WHERE name LIKE '%s';" % (name))
        return self.cr.fetchone()

    def create_batch(self, values):
        self.cr.execute("INERT INTO op_batch "
                        "(name, code, course_id, start_date,"
                        " end_date, coordinator, campus_id, date_diplomas,"
                        " academic_year, days_week, schedule, class_place, "
                        "students_limit, type_practices) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
                        "%s, %s);" % (values[0], values[1], values[2], values[3], values[4],
                                      values[5], values[6], values[7], values[8], values[9],
                                      values[10], values[11], values[12], values[13])
                        )
    def get_country_by_name(self, name):
        self.cr.execute("SELECT id FROM res_country WHERE name LIKE '%s';" % (name))
        return self.cr.fetchone()

    def get_partner_by_email_or_name(self, email, name):
        self.cr.execute("SELECT id FROM res_partner WHERE name LIKE '%s' or email LIKE '%s';" % (name, email))
        return self.cr.fetchone()

    def create_partner(self, values):
        self.cr.execute("INERT INTO res_partner "
                        "(name, email, phone, mobile, street,"
                        "zip, city, country_id) VALUES (%s, %s, %s, %s,"
                        " %s, %s, %s, %s);" % (values[0], values[1], values[2],
                                               values[3], values[4], values[5],
                                               values[6], values[7])
                        )

    def create_faculty(self, values):
        self.cr.execute("INSERT INTO op_faculty "
                        "(first_name, last_name, email, phone, "
                        "birth_date, gender, nationality, partner_id,"
                        " nifp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);" % (values[0], values[1], values[2],
                                                                                values[3], values[4], values[5],
                                                                                values[6], values[7], values[8])
                        )

    def create_record(self, table, records):
        marks = ', '.join('?' * len(records))
        query = "INSERT INTO %s (%s) VALUES (%s);" % (table, marks, marks)
        self.cr.execute(query, marks.keys() + marks.values())
        self.cr.commit()
