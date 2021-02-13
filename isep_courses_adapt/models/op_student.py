import traceback

from odoo import fields, api, models
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from .op_sql import SQL
from .op_moodle import Moodle
from .moodle import MoodleLib
import datetime
import logging
import os
from .op_mysql import MYSQL
import ast

logger = logging.getLogger(__name__)


class OpStudent(models.Model):
    _name = 'op.student'
    _inherit = ['op.student', 'mail.thread']

    campus_id = fields.Many2one('op.campus', string='Campus')
    place_birth = fields.Char(string='Place of birth', size=200)
    uvic_program = fields.Boolean(string='UVIC Program',
                                  default=False)
    # rvoe_program = fields.Boolean(string='SEPYC Program',default=False)
    sepyc_program = fields.Boolean(string='SEPYC Program',
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
    delay = fields.Boolean(string="Delay")
    status_documentation = fields.Selection([
        ('complete', 'Completado'),
        ('in process', 'En proceso'),
        ('Not send', 'No enviada')
    ], 'Status documentation')
    partner_id = fields.Many2one('res.partner', 'Partner', required=False)
    # document_ids = fields.One2many("op.gdrive.documents", "partner_id",
    #                              string="Documentation")
    access_ids = fields.One2many("op.student.access", "student_id",
                                 string="Access")
    admission_ids = fields.One2many("op.admission", "student_id",
                                    string="Admissions")
    admission_count = fields.Integer(compute='_compute_admission_count',
                                     default=0)
    exam_attendees_ids = fields.One2many("op.exam.attendees", "student_id",
                                         string="Exam attendees")
    exam_attendees_count = fields.Integer(
        compute='_compute_exam_attendees_count', default=0)
    last_access = fields.Char(String='Last access',
                              compute='_get_last_access',
                              readonly=True)
    student_state = fields.Selection(
        [('draft', 'Draft'), ('progress', 'In progress'),
         ('done', 'Done'), ('cancel', 'Cancelled')], string='Student state',
        default='progress', store=True, compute='_compute_student_state')

    status_student = fields.Selection(
        [('valid', 'Valid'), ('graduate', 'Graduate'),
         ('low', 'Low')], default='valid', string="Student Status",
        store=True, compute='_compute_determine_status', translate=True)
    type_of_course_taken = fields.Many2many(
        comodel_name='op.course.type',
        string='Type of course taken',
        translate=True, store=True,
        compute='_compute_determine_type_of_course')
    cgi_client_id = fields.Integer(string='Cgi client')
    unsubscribed_date = fields.Date(string="Unsubscribed date",
                                    store=True,
                                    related='admission_ids.unsubscribed_date')

    _sql_constraints = [(
        'unique_n_id',
        'unique(n_id)',
        'N_ID Number must be unique per student!'
    )]

    def _compute_determine_type_of_course(self):
        for student in self:
            for admission in student.admission_ids:
                if admission.course_id.course_type_id not in \
                        student.type_of_course_taken and \
                        admission.course_id.course_type_id.id:
                    student.update({
                        'type_of_course_taken': [
                            (4, admission.course_id.course_type_id.id)]
                    })

    def _compute_determine_status(self):
        for student in self:
            for admission in student.admission_ids:
                if admission.due_date:
                    if fields.Date.today() >= admission.due_date:
                        student.status_student = 'graduate'
                    else:
                        student.status_student = 'valid'
                else:
                    student.status_student = 'valid'
                if admission.unsubscribed_date:
                    if fields.Date.today() >= admission.unsubscribed_date:
                        student.status_student = 'low'
                    else:
                        student.status_student = 'valid'
                else:
                    student.status_student = 'valid'

    def _compute_admission_count(self):
        """Compute the number of distinct admissions linked to the batch."""
        for student in self:
            student.admission_count = len(student.admission_ids)

    @api.multi
    def _compute_exam_attendees_count(self):
        for student in self:
            student.exam_attendees_count = len(student.exam_attendees_ids)

    def action_open_admissions(self):
        """Display the linked admissions and adapt the view to the number of
        records to display."""
        self.ensure_one()
        admissions = self.admission_ids
        action = self.env.ref('openeducat_admission.act_open_op_admission_view').read()[0]
        if len(admissions) > 1:
            action['domain'] = [('id', 'in', admissions.ids)]
        elif len(admissions) == 1:
            form_view = [(self.env.ref(
                'openeducat_admission.view_op_admission_form').id, 'form')]
            if 'views' in action:
                logger.info("=== LINE 52 ===")
                action['views'] = form_view + [(state, view) for state, view in
                                               action['views'] if
                                               view != 'form']
            else:
                logger.info("=== LINE 55 ===")
                action['views'] = form_view
            action['res_id'] = admissions.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_open_exam_attendees(self):
        """Display the linked exam attendees and adapt the view to the
        number of records to display."""
        self.ensure_one()
        exam_attendees = self.exam_attendees_ids
        action = self.env.ref(
            'isep_courses_adapt.act_exam_attendees_view_grouped').read()[0]
        if len(exam_attendees) > 1:
            action['domain'] = [('id', 'in', exam_attendees.ids)]
        elif len(exam_attendees) == 1:
            form_view = [(self.env.ref(
                'openeducat_exam.view_op_exam_attendees_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in
                                               action['views'] if
                                               view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = exam_attendees.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _compute_student_state(self):
        for student in self:
            state = 'done'
            for admission in student.admission_ids:
                if not admission.due_date:
                    state = 'draft'
                elif admission.due_date and admission.due_date >= fields.Date.today():
                    state = 'progress'
            student.student_state = state

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

    @staticmethod
    def equal_datetimes_YYMMDDHHmm(ddtime1, ddtime2):
        return isinstance(ddtime1, datetime.datetime) and \
               isinstance(ddtime2, datetime.datetime) and \
               ddtime1.replace(minute=0, second=0, microsecond=0) == \
               ddtime2.replace(minute=0, second=0, microsecond=0)

    def update_access(self, rows):
        logger.info("**************************************")
        logger.info("update_access")
        logger.info("**************************************")
        for row in rows:
            if 'idnumber' in row or 'id' in row:
                try:
                    student = self.search([('moodle_id', '=', row['id'])])
                    if not isinstance(row['lastaccess'], int):
                        continue
                    last_access = datetime.datetime.utcfromtimestamp(
                        row['lastaccess'])
                    if len(student) == 1:
                        access_values = {
                            'student_id': student.id,
                            'student_access': last_access
                        }
                        _access = self.env['op.student.access'].search(
                            [('student_id', '=', student.id)])
                        if len(_access) > 0:
                            _access = _access[-1]
                        if not self.equal_datetimes_YYMMDDHHmm(last_access,
                                                               _access.student_access):
                            self.env['op.student.access'].create(access_values)
                            logger.info('Student access created')
                    elif len(student) > 1:
                        logger.info(row)
                except Exception as e:
                    logger.info(e)
                    continue

    def import_recent_student_access(self, days=1):
        logger.info("**************************************")
        logger.info("import recent student access")
        logger.info("**************************************")

        mqsl = MYSQL()

        rows = mqsl.query_recent_access()

        if len(rows) > 0:
            self.update_access(rows)

        logger.info("********************************************")
        logger.info("End of script: import recent student access")
        logger.info("********************************************")

    def import_all_student_access(self):
        logger.info("**************************************")
        logger.info("import all student access")
        logger.info("**************************************")
        moodle = self.env['moodle']
        rows = Moodle.get_last_access_cron(moodle)
        for row in rows:
            try:
                students = self.search(
                    [('moodle_id', '=', row['id'])])
                if not isinstance(row['lastaccess'], int):
                    continue
                last_access = datetime.datetime.utcfromtimestamp(
                    row['lastaccess'])
                if len(students) > 0:
                    for student in students:
                        access_values = {
                            'student_id': student.id,
                            'student_access': last_access
                        }
                        _access = self.env['op.student.access'].search(
                            [('student_id', '=', student.id)])
                        if len(_access) > 0:
                            _access = _access[-1]
                        if not self.equal_datetimes_YYMMDDHHmm(last_access,
                                                               _access.student_access):
                            self.env['op.student.access'].create(
                                access_values)
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
        if self.document_number or self.moodle_id != 0:
            moodle = self.env['moodle']
            rows = Moodle.get_last_access(moodle, 'id',
                                          self.moodle_id)
            logger.info(rows)
            for row in rows:
                try:
                    if not isinstance(row['lastaccess'], int):
                        continue
                    if row['lastaccess'] == 0:
                        logger.info(row['lastaccess'])
                        continue
                    last_access = datetime.datetime.utcfromtimestamp(
                        row['lastaccess'])
                    access_values = {
                        'student_id': self.id,
                        'student_access': last_access
                    }
                    logger.info("lastaccess: {}".format(row['lastaccess']))
                    logger.info("access_values: {}".format(access_values))
                    _access = self.env['op.student.access'].search(
                        [('student_id', '=', self.id)])
                    if len(_access) > 0:
                        _access = _access[-1]
                    if self.document_number in (
                    'AU449596', 'G08428409', '45522791', '1030639754'):
                        logger.info(
                            '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                        logger.info(
                            'last_access:{} _access:{}'.format(last_access,
                                                               _access.student_access))
                        logger.info(
                            '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                    if not self.equal_datetimes_YYMMDDHHmm(last_access,
                                                           _access.student_access):
                        self.env['op.student.access'].create(access_values)
                except Exception as e:
                    logger.info(e)
                    traceback.print_exc()
                    continue

    @staticmethod
    def greeting(gender):
        resp = 'Apreciado(a)'
        try:
            if gender == 'f':
                resp = 'Apreciada'
            if gender == 'm':
                resp = 'Apreciado'
        except Exception as e:
            logger.info(e)
        return resp

    def get_days_without_access(self, id):
        return self.env['op.student.access']. \
            search([('student_id', '=', id)])[-1][0]. \
            last_access.split('días')[0].strip()

    def cron_send_email(self):
        logger.info("**************************************")
        logger.info("send email")
        logger.info("**************************************")

        int_break = 0
        tname = {5: 'Email Student Access 5 days',
                 12: 'Email Student Access 12 days',
                 20: 'Email Student Access 20 days',
                 40: 'Email Student Access 40 days',
                 70: 'Email Student Access 70 days',
                 80: 'Email Student Access 80 days',
                 100: 'Email Student Access 100 days'}



        for student in self.env['op.student'].search([]):
            try:
                last_access = self.env['op.student.access'].search(
                    [('student_id', '=', student.id)])
                if len(last_access) > 0:
                    last_access = last_access[-1].last_access
                    if 'años' in last_access:
                        continue
                    if 'días' in last_access:
                        days = self.get_days_without_access(student.id)
                        days = ast.literal_eval(days)
                        if days in (5, 12, 20, 40, 70, 80, 100):
                            #Estamos tomando el ultimo template porque estan duplicados
                            template = self.env['mail.template'].search(
                                [('name', '=', tname[days])])
                            if template:
                                template.send_mail(student.id, force_send=True,
                                                   raise_exception=True)
                            if days == 100:
                                template = self.env['mail.template'].search([
                                    ('name', '=',
                                     'Email Student Access Final Message')])
                                if template:
                                    template.send_mail(student.id,
                                                       force_send=True,
                                                       raise_exception=True)
                            logger.info('email sent to {}'.format(
                                student.first_name))
            except Exception as e:
                logger.info(e)

        logger.info("**************************************")
        logger.info("End of script: send email")
        logger.info("**************************************")

    def send_email_back(self):
        logger.info("**************************************")
        logger.info("send email")
        logger.info("**************************************")
        template = self.env['mail.template'].search(
            [('name', '=', 'Email Student Access')])
        int_break = 0
        if template:
            int_break = 0
            for student in self.env['op.student'].search([]):
                try:
                    last_access = self.env['op.student.access'].search([(
                        'student_id', '=', student.id)])
                    if len(last_access) > 0:
                        last_access = last_access[-1].last_access
                        if 'años' in last_access:
                            continue
                        if 'días' in last_access:
                            days = self.get_days_without_access(student.id)
                            days = ast.literal_eval(days)
                            logger.info('dias:{}'.format(days))
                            if days in (5, 12, 20, 40, 70, 80, 100):
                                template.send_mail(student.id, force_send=True,
                                                   raise_exception=True)
                                logger.info('email sended to {}'.format(
                                    student.first_name))
                except Exception as e:
                    logger.info(e)

                if int_break == 100 and os.name != "posix":
                    break
                int_break += 1
        logger.info("**************************************")
        logger.info("End of script: send email")
        logger.info("**************************************")

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
                    country = self.env['res.country'].search(
                        [('name', 'ilike', app_country.country or '')],
                        limit=1)
                    partner = self.env['res.partner'].search(
                        [('email', '!=', False),
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
                        partner = self.env['res.partner'].create(
                            partner_values)
                    campus = self.env['op.campus'].search(
                        [('code', '=', student.Sede)], limit=1)
                    document_type = self.env['op.document.type'].search(
                        [('code', '=', student.TipoDocumento)], limit=1)
                    study_type = self.env['op.study.type'].search(
                        [('code', '=', student.TipoEstudios)], limit=1)
                    university = self.env['op.university'].search(
                        [('code', '=', student.TipoEstudios)], limit=1)
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

                    logger.info(student_values)
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

    def import_student_course_rel(self):
        s = SQL()
        logger.info("**************************************")
        logger.info("On import students courses relations")
        logger.info("**************************************")
        offset = self.env['op.student.course'].search_count([])
        rows = s.get_all_batch(offset)
        int_break = 0
        for row in rows:
            try:
                student = self.env['op.student'].search(
                    [('gr_no', '=', row.gr_no)], limit=1)
                course = self.env['op.course'].search(
                    [('code', '=', row.code)], limit=1)
                batch = self.env['op.batch'].search(
                    [('code', '=', row.batch)], limit=1)

                if len(student) > 0 and len(course) > 0 and len(batch) > 0:
                    exist_rel = self.env['op.student.course'].search(
                        [('student_id', '=', student.id),
                         ('course_id', '=', course.id),
                         ('batch_id', '=', batch.id)], limit=1)
                    if len(exist_rel) == 0:
                        values = {
                            'student_id': student.id,
                            'course_id': course.id,
                            'batch_id': batch.id,
                            'roll_number': row.gr_no
                        }
                        student_course = self.env['op.student.course'].create(
                            values)
                        # student.update(
                        #     {'course_detail_ids': [(4, student_course.id)]})
                        logger.info('Student with n_id {0} updated'.format(
                            student.id))

                #if int_break == 50 and os.name != "posix":
                 #   break
                #int_break += 1

            except Exception as e:
                logger.info(e)
                traceback.print_exc()
                continue

    def import_student_subjects_rel(self):
        s = SQL()
        logger.info("**************************************")
        logger.info("On import students subjects relations")
        logger.info("**************************************")
        students = self.env['op.student'].search([])
        for student in students:
            for course in student.course_detail_ids:
                subjects = s.get_all_subjects_by_course_student(
                    course.batch_id.code, student.gr_no)
                for subject in subjects:
                    subject_tb = self.env['op.subject'].search(
                        [('code', '=', subject.CodAsignatura)], limit=1)
                    for tb in subject_tb:
                        course.update({'subject_ids': [(4, tb.id)]})
                        logger.info("Write subject %s for student ID %s" % (
                            tb.id, student.id))

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
        file_list = drive.ListFile(
            {'q': "'root' in parents and trashed=false"}).GetList()
        for rec in self:
            documents = self.env['op.gdrive.documents'].search(
                [('partner_id', '=', rec.partner_id.id)])
            delete_folder = False
            for doc in documents:
                doc.unlink()
        self.env['op.admission'].search([('student_id', '=', self.id)]).write(
            {'is_student': False})
        self.env['op.subject.registration'].search([('student_id', '=',
                                                     self.id)]).unlink()
        res = super(OpStudent, self).unlink()
        return res

    def import_log_history(self):
        s = SQL()
        logger.info("**************************************")
        logger.info("On import students history")
        logger.info("**************************************")
        historys = s.get_all_history()
        for history in historys:
            if history.Observaciones != '':
                body = """<p>%s - %s</p>
                 <p>%s</p>""" % (history.Fecha, history.Usuario, history.Observaciones)
                student = self.search([('gr_no', '=', history.N_Id)])
                if len(student) > 0:
                    message = self.env['mail.message'].search([('body', '=', body),('model','=', 'op.student'),
                                                                ('res_id', '=', student.id)], limit=1)
                    if len(message) > 0:
                        logger.info("Message already exist id %s" % message.id)
                        continue
                    else:
                        student.message_post(body=body)
                        message = self.env['mail.message'].search([('body', '=', body),('model','=', 'op.student'),
                                                                ('res_id', '=', student.id)], limit=1)
                        message.write({
                            'date' : history.Fecha
                            })
                        logger.info("Message register for student gr_no %s" % student.gr_no)
                else:
                    logger.info("Student not exist gr_no %s" % history.N_Id)
        logger.info("**************************************")
        logger.info("End import students history")
        logger.info("**************************************")

    def update_university(self):
        logger.info("**************************************")
        logger.info("update_university")
        logger.info("**************************************")
        s = SQL()
        offset = 0
        alumnos = s.get_all_students(offset=offset)
        int_break = 0
        for alumno in alumnos:
            try:
                student = self.search([('n_id', '=', alumno.N_Id)])
                logger.info('id:{} name:{}'.format(student.id, student.name))
                if len(student) == 0:
                    student = self.search([('gr_no', '=', alumno.N_Id)])
                if len(student) == 0:
                    continue
                university = self.env['op.university'].search(
                    [('code', '=', alumno.Universidad)])
                if len(university) != 0:
                    student.university_id = university.id
                    logger.info(
                        'Student [id:{} name:{}] University [code:{} id:{}]'. \
                            format(student.id, student.name, university.code,
                                   university.id))
                if int_break == 1000 and os.name != "posix":
                    break
                int_break += 1
            except Exception as e:
                logger.info(e)
                continue

    def get_moodle_id(self):
        moodle = MoodleLib()
        user_moodle = moodle.get_user_by_field(field="email",
                                               value=self.partner_id.email)
        return user_moodle.get('id') if 'id' in user_moodle else False
