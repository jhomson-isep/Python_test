# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

logger = logging.getLogger(__name__)


class UvicStudent(models.TransientModel):
    _name = 'uvic.student'
    uvic_documentation = fields.Boolean(string="Documentación Uvic", default=True)

    def print_uvic_report(self):
        data = {
            'model': 'uvic.student',
            'form': self.read()[0]
        }

        logger.info(self.read()[0])

        students_bool = data['form']['uvic_documentation']
        students = self.env['op.student'].search([('uvic_documentation', '=', students_bool)])
        print(students)

        students_list = []
        for student in students:
            vals = {
                'document_number': student.document_number,
                'first_name': student.first_name,
                'document_type_id': student.document_type_id,
                'last_name': student.last_name,
                'gender': student.gender,
                'nationality': student.nationality,
                'birth_date': student.birth_date,
                'email': student.email,
                'street': student.street,
                'country_id': student.country_id,
                'zip': student.zip,
                'mobile': student.mobile
            }
            students_list.append(vals)

        data['students'] = students_list

        return self.env.ref('isep_openeducat_reports.report_uvic_students').report_action(self, data=data)

