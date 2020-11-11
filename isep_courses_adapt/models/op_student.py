from odoo import fields, api, models
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from .op_sql import SQL
from .op_moodle import Moodle
import datetime
from dateutil.relativedelta import relativedelta
import logging
import os
import mysql.connector
from mysql.connector import errorcode

logger = logging.getLogger(__name__)


class OpStudent(models.Model):
    _name = 'op.student'
    _inherit = ['op.student', 'mail.thread']

    campus_id = fields.Many2one('op.campus', string='Campus')
    uvic_documentation = fields.Boolean(string='UVIC Documentation',
                                        default=False)
    rvoe_documentation = fields.Boolean(string='RVOE Documentation',
                                        default=False)
    curp = fields.Char(string='CURP', size=20)
    year_end_studies = fields.Integer(string='Year of completion of studies')
    document_type_id = fields.Many2one('op.document.type',
                                       string='Document type')
    document_number = fields.Char(string='Document number', size=32)
    contact_type_id = fields.Many2one('op.contact.type', string='Contact type')
    study_type_id = fields.Many2one('op.study.type', string='Study type')
    university_id = fields.Many2one('op.university', string='University')
    n_id = fields.Char("N_ID", size=20)
    moodle_id = fields.Integer(string='Moodle ID')
    moodle_user = fields.Char(string='Moodle user', size=128)
    moodle_pass = fields.Char(string='Moodle Password', size=24)
    partner_id = fields.Many2one('res.partner', 'Partner', required=False)
    document_ids = fields.One2many("op.student.documents", "student_id",
                                   string="Documentation")
    access_ids = fields.One2many("op.student.access", "student_id",
                                 string="Access")
    last_access = fields.Char(String='Last access',
                              compute='_get_last_access',
                              readonly=True)

    _sql_constraints = [(
        'unique_n_id',
        'unique(n_id)',
        'N_ID Number must be unique per student!'
    )]

    def _get_last_access(self):
        for record in self:
            last_access = record.env['op.student.access'].search(
                [('student_id', '=', record.id)], order='id desc', limit=1)
            if last_access.student_access:
                access_ago = fields.Datetime.today() - last_access.student_access
                minutes, seconds = divmod(access_ago.seconds, 60)
                hours, minutes = divmod(minutes, 60)
                access_string = "Hace "
                if access_ago.days > 0:
                    access_string += "{0} días ".format(access_ago.days)
                if hours > 0:
                    access_string += "{0} horas ".format(hours)
                if minutes > 0:
                    access_string += "{0} minutos ".format(minutes)
                record.last_access = access_string
            else:
                record.last_access = "Nunca"

    def update_access(self, rows):
        for row in rows:
            if 'idnumber' in rows and row['idnumber'] != '':
                try:
                    student = self.search(
                        [('document_number', '=', row['idnumber'])])
                    last_access = datetime.datetime.utcfromtimestamp(
                        row['lastaccess'])
                    if len(student) == 1:
                        acces_values = {
                            'student_id': student.id,
                            'student_access': last_access
                        }
                        _access = self.env['op.student.access'].search(
                            [('student_id', '=', student.id)], limit=1)
                        year = _access.student_access.year
                        month = _access.student_access.month
                        day = _access.student_access.day
                        if not (last_access.year == year and last_access.month == month and last_access.day == day):
                            self.env['op.student.access'].create(acces_values)
                except Exception as e:
                    logger.info(e)
                    continue

    def import_recent_student_access(self, days=1):
        logger.info("**************************************")
        logger.info("import recent student access")
        logger.info("**************************************")
        config = {
            'user': 'odoo',
            'password': 'Iseplatam2020',
            'host': '192.168.0.153',
            'database': 'moodle'
        }
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=days)
        today = today.strftime('%Y-%m-%d')
        yesterday = yesterday.strftime('%Y-%m-%d')
        try:
            cnx = mysql.connector.connect(**config)
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
                    logger.info({'id': id, 'idnumber': idnumber, 'lastaccess': lastaccess})
                    rows.append({'id': id, 'idnumber': idnumber, 'lastaccess': lastaccess})

            self.update_access(rows)

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            cnx.close()

        logger.info("********************************************")
        logger.info("End of script: import recent student access")
        logger.info("********************************************")

    def import_all_student_access(self):
        logger.info("**************************************")
        logger.info("import all student access")
        logger.info("**************************************")
        moodle = self.env['moodle']
        rows = Moodle.get_last_access_cron(moodle)
        for dic in rows:
            if 'idnumber' in dic:
                try:
                    student = self.search(
                        [('document_number', '=', dic['idnumber'])])
                    last_access = datetime.datetime.utcfromtimestamp(
                        dic['lastaccess'])
                    if len(student) == 1:
                        acces_values = {
                            'student_id': student.id,
                            'student_access': last_access
                        }
                        self.env['op.student.access'].create(acces_values)
                except Exception as e:
                    logger.info(e)
                    continue
        logger.info("*****************************************")
        logger.info("End of script: import all students access")
        logger.info("*****************************************")


    def import_student_access(self):
        logger.info("**************************************")
        logger.info("import student access")
        logger.info("**************************************")
        moodle = self.env['moodle']
        if self.document_number:
            rows = Moodle.get_last_access(moodle, 'idnumber',
                                          self.document_number)
            for row in rows:
                try:
                    last_access = datetime.datetime.utcfromtimestamp(
                        row['lastaccess'])
                    acces_values = {
                        'student_id': self.id,
                        'student_access': last_access
                    }
                    _access = self.env['op.student.access'].search(
                        [('student_id', '=', self.id)], limit=1)
                    year = _access.student_access.year
                    month = _access.student_access.month
                    day = _access.student_access.day

                    if not (last_access.year == year and last_access.month == month and last_access.day == day):
                        self.env['op.student.access'].create(acces_values)
                except Exception as e:
                    logger.info(e)
                    continue

    def import_students(self):
        s = SQL()
        logger.info("**************************************")
        logger.info("On import students")
        logger.info("**************************************")
        offset = self.search_count([])
        rows = s.get_all_students(offset=offset)
        int_break = 0
        for student in rows:
            try:
                existent_student = self.search([('n_id', '=', student.N_Id)])
                if len(existent_student) < 1:
                    app_country = s.get_country_by_nid(student.N_Id)
                    country = self.env['res.country'].search([('name', 'ilike', app_country.country or '')], limit=1)
                    partner = self.env['res.partner'].search([('email', '!=', False),
                                                              ('email', '=', student.EMail)], limit=1)
                    if not partner.id:
                        partner_values = {
                            'name': student.Nombre + " " + student.Apellidos,
                            'email': student.EMail,
                            'phone': student.Telefono,
                            'mobile': student.Telefono,
                            'street_name': student.Direccion,
                            'zip': student.CodPostal or None,
                            'city': student.Poblacion,
                            'country_id': country.id,
                            'vat': student.CURPMx or student.DNI,
                            'is_student': True
                        }
                        partner = self.env['res.partner'].create(partner_values)
                    campus = self.env['op.campus'].search([('code', '=', student.Sede)], limit=1)
                    document_type = self.env['op.document.type'].search([('code', '=', student.TipoDocumento)], limit=1)
                    study_type = self.env['op.study.type'].search([('code', '=', student.TipoEstudios)], limit=1)
                    university = self.env['op.university'].search([('code', '=', student.TipoEstudios)], limit=1)
                    if student.Sexo == 'H':
                        gender = 'm'
                    elif student.Sexo == 'M':
                        gender = 'f'
                    else:
                        gender = 'o'

                    student_values = {
                        'first_name': student.Nombre,
                        'last_name': student.Apellidos,
                        'email': student.EMail,
                        'mobile': student.Telefono,
                        'partner_id': partner.id or None,
                        'birth_date': student.FechaNacimiento or fields.Date.today(),
                        'gender': gender,
                        'nationality': country.id or None,
                        'n_id': student.N_Id,
                        'gr_no': student.N_Id,
                        'campus_id': campus.id or None,
                        'curp': student.CURPMx,
                        'year_end_studies': student.AnyFinalizacionEstudios,
                        'document_type_id': document_type.id or None,
                        'document_number': student.DNI,
                        'study_type_id': study_type.id or None,
                        'university_id': university.id or None,
                        'moodle_id': student.IDMoodle,
                        'moodle_user': student.Usuario
                    }

                    # logger.info(student_values)
                    res = super(OpStudent, self).create(student_values)
                    logger.info('Student with n_id {0} created'.format(
                        student_values['n_id']))

                    if int_break == 1000 and os.name != "posix":
                        break
                    int_break += 1

            except Exception as e:
                logger.info(e)
                continue

        logger.info("**************************************")
        logger.info("End of script: import students")
        logger.info("**************************************")

    def Gauth(self):
        logger.info(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.dirname(os.path.abspath(__file__))
        credentials_file = model_path + "/drive/credentials.txt"
        drive_config_file = model_path + '/drive/client_secrets.json'
        GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = drive_config_file
        gauth = GoogleAuth()
        # Try to load saved client credentials
        gauth.LoadCredentialsFile(credentials_file)
        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved credentials
            gauth.Authorize()
        # Save the current credentials to a file
        gauth.SaveCredentialsFile(credentials_file)
        return gauth

    def unlink(self):
        gauth = self.Gauth()
        drive = GoogleDrive(gauth)
        file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for rec in self:
            documents = self.env['op.student.documents'].search([('student_id', '=', rec.id)])
            delete_folder = False
            for doc in documents:
                doc.unlink()
        res = super(OpStudent, self).unlink()
        return res
