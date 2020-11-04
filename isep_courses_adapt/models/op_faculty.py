from odoo import models, fields
from datetime import date
from .op_sql import SQL
import logging
import os

logger = logging.getLogger(__name__)


class OpFaculty(models.Model):
    _inherit = 'op.faculty'

    job_title = fields.Char(string='Job title', size=128)
    specialty = fields.Char(string='Specialty', size=128)
    workplace_ids = fields.Many2many('op.workplace', string='Workplace')
    nifp = fields.Char(string='NIFP', size=20)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], 'Gender', required=True)
    document_ids = fields.One2many("op.student.documents", "faculty_id", String="Documentation")

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
