from odoo import fields, api, models
from .op_sql import SQL
from .op_moodle import Moodle
import logging
import datetime
import os

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
    #021120
    access_ids = fields.One2many("op.student.access", "student_id",
                                   string="Access")

    _sql_constraints = [(
        'unique_n_id',
        'unique(n_id)',
        'N_ID Number must be unique per student!'
    )]

    def import_all_student_access(self):
        logger.info("**************************************")
        logger.info("import all student access")
        logger.info("**************************************")
        moodle = self.env['moodle']
        rows = Moodle.get_last_access_cron(moodle)
        for dic in rows:
            if 'idnumber' in dic:
                student=self.search([('document_number','=',dic['idnumber'])])
                ult_access = datetime.datetime.utcfromtimestamp(dic['lastaccess'])
                if len(student)>0:
                    acces_values = {
                        'student_id': student.id,
                        'student_access': ult_access
                    }
                    self.env['op.student.access'].create(acces_values)

    def import_student_access(self):
        logger.info("**************************************")
        logger.info("import student access")
        logger.info("**************************************")
        moodle=self.env['moodle']
        if(not(self.document_number==False)):
            rows = Moodle.get_last_access(moodle, 'idnumber', self.document_number)
            for row in rows:
                ult_access=datetime.datetime.utcfromtimestamp(row['lastaccess'])
                acces_values = {
                    'student_id': self.id,
                    'student_access': ult_access
                }
                _access=self.env['op.student.access'].search([('student_id', '=', self.id)], limit=1)
                if(_access.student_access!=ult_access):
                    self.env['op.student.access'].create(acces_values)

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
                    print(res)
                    logger.info('Student with n_id {0} created'.format(
                        student_values['n_id']))

                    if int_break == 100 and os.name != "posix":
                        break
                    int_break += 1

            except Exception as e:
                logger.info(e)
                continue

        logger.info("**************************************")
        logger.info("End of script: import students")
        logger.info("**************************************")
