from docutils.nodes import docinfo

from odoo import models, fields
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import date
from .op_sql import SQL
import logging
import os

logger = logging.getLogger(__name__)


class OpFaculty(models.Model):
    _inherit = 'op.faculty'

    job_title = fields.Char(string='Job title', size=128)
    bank_teacher_id = fields.Many2many('res.partner.bank')
    specialty = fields.Char(string='Specialty', size=128)
    workplace_ids = fields.Many2many('op.workplace', string='Workplace')
    place_birth = fields.Char(string='Place of birth', size=200)
    nifp = fields.Char(string='NIFP', size=20)
    document_type_id = fields.Many2one('op.document.type',
                                       string='Document type')
    document_number = fields.Char(string='Document number', size=32)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], 'Gender', required=True)
    document_ids = fields.One2many("op.student.documents",
                                   "faculty_id",
                                   String="Documentation")
    company_id = fields.Many2one('res.company', string="Company")
    category_id = fields.Many2one('op.category', string="Teacher Categories")
    street_job = fields.Char()
    street2_job = fields.Char()
    zip_job = fields.Char(change_default=True)
    city_job = fields.Char()
    state_job_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                                   domain="[('country_id', '=?', country_job_id)]")
    country_job_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    @staticmethod
    def add_years(d, years):
        """Return a date that's `years` years after the date (or datetime)
        object `d`. Return the same calendar date (month and day) in the
        destination year, if it exists, otherwise use the following day
        (thus changing February 29 to March 1).
        """
        try:
            return d.replace(year=d.year + years)
        except ValueError:
            return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

    def import_faculties(self):
        s = SQL()
        logger.info("**************************************")
        logger.info("On import faculties")
        logger.info("**************************************")
        offset = self.search_count([])
        rows = s.get_all_faculties(offset=offset)
        int_break = 0
        for faculty in rows:
            try:
                existent_faculty = self.search([('nifp', '=', faculty.NIFP)])
                if len(existent_faculty) < 1:
                    app_country = s.get_country_by_nifp(faculty.NIFP)
                    country = self.env['res.country'].search(
                        [('name', 'ilike', app_country.country or '')],
                        limit=1)
                    partner = self.env['res.partner'].search(
                        ['|', ('email', '=', faculty.EMail),
                         ('name', 'ilike', faculty.Nombre + " " +
                          faculty.Apellidos)], limit=1)
                    if not partner.id:
                        partner_values = {
                            'name': "{0} {1}".format(faculty.Nombre,
                                                     faculty.Apellidos),
                            'email': faculty.EMail,
                            'phone': faculty.Telefono,
                            'mobile': faculty.Telefono,
                            'street_name': faculty.Direccion,
                            'zip': faculty.CodPostal or None,
                            'city': faculty.Poblacion,
                            'country_id': country.id
                        }
                        partner = self.env['res.partner'].create(
                            partner_values)

                    faculty_values = {
                        'first_name': faculty.Nombre,
                        'last_name': faculty.Apellidos,
                        'email': faculty.EMail,
                        'phone': faculty.Telefono,
                        'birth_date': fields.Date.today(),
                        'gender': 'other',
                        'nationality': country.id or None,
                        'partner_id': partner.id,
                        'nifp': faculty.NIFP
                    }

                    res = super(OpFaculty, self).create(faculty_values)
                    print(res)
                    logger.info('Faculty with NIFP {0} created'.format(
                        faculty_values['nifp']))

                int_break += 1
                if int_break == 50 and os.name != "posix":
                    break

            except Exception as e:
                logger.info(e)
                int_break += 1
                continue

        logger.info("**************************************")
        logger.info("End of script: import faculties")
        logger.info("**************************************")

    def import_subjects_faculty(self):
        s = SQL()
        logger.info("**************************************")
        logger.info("On import faculties subjects relations")
        logger.info("**************************************")
        facultys = self.env['op.faculty'].search([])
        for faculty in facultys:
            subjects = s.get_all_subjects_faculty(faculty.nifp)
            for subject in subjects:
                subject_tb = self.env['op.subject'].search(['code', '=', subject.CodAsignatura])
                for subj in subject_tb:
                    faculty.update({'faculty_subject_ids': [(4, subj.id)]})
                    logger.info("Update Subject {0} for Faculty {1}".format(faculty.nifp, subj.code))

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
            documents = self.env['op.student.documents'].search([('faculty_id', '=', rec.id)])
            for doc in documents:
                doc.unlink()
        res = super(OpFaculty, self).unlink()
        return res
