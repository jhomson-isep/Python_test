from odoo import models

class StudentXlsx(models.AbstractModel):
    _name = 'report.isep_openeducat_reports.report_uvic_students'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, students):
        #students = self.env['op.student'].sudo().search([('uvic_documentation', '=', True)])

        sheet = workbook.add_worksheet('UVIC Report')
        bold = workbook.add_format({'bold': True})

        #Titulos
        sheet.write(0, 0, 'DNI_PASAPORTE', bold)
        sheet.write(0, 1, 'TIPO_DOC_ID', bold)
        sheet.write(0, 2, 'NOM_ALUMNO', bold)
        sheet.write(0, 3, 'APE1_ALUMNO', bold)
        sheet.write(0, 4, 'APE2_ALUMNO', bold)
        sheet.write(0, 5, 'SEXO_ALUMNO', bold)
        sheet.write(0, 6, 'COD_PAIS_NACION', bold)
        sheet.write(0, 7, 'FECHA_NAC_ALUMNO', bold)
        sheet.write(0, 8, 'COD_PAIS_NACIM', bold)
        sheet.write(0, 9, 'COD_POSTAL_NACIM', bold)
        sheet.write(0, 10, 'ORD_LOCALIZ_NACIM', bold)
        sheet.write(0, 11, 'CORREO_ELEC_2', bold)
        sheet.write(0, 12, 'DOMICILIO_HABIT', bold)
        sheet.write(0, 13, 'COD_PAIS_HABIT', bold)
        sheet.write(0, 14, 'COD_POSTAL_HABIT', bold)
        sheet.write(0, 15, 'ORD_LOCALIZ_HABIT', bold)
        sheet.write(0, 16, 'TELEFONO_HABIT', bold)
        sheet.write(0, 17, 'TELEFONO2_HABIT', bold)
        sheet.write(0, 18, 'Codi Assignatures', bold)

        i = 1
        for obj in students:
            sheet.write(i, 0, obj.document_number)
            sheet.write(i, 1, obj.document_type_id.code)
            sheet.write(i, 2, obj.first_name)
            sheet.write(i, 3, obj.last_name)
            sheet.write(i, 4, obj.last_name)
            sheet.write(i, 5, obj.gender)
            sheet.write(i, 6, obj.nationality.code)
            sheet.write(i, 7, obj.birth_date)
            sheet.write(i, 8, obj.nationality.code)
            sheet.write(i, 9, '')
            sheet.write(i, 10, 0)
            sheet.write(i, 11, obj.email)
            sheet.write(i, 12, obj.street)
            sheet.write(i, 13, obj.country_id.code)
            sheet.write(i, 14, obj.zip)
            sheet.write(i, 15, 0)
            sheet.write(i, 16, obj.mobile)
            sheet.write(i, 17, obj.mobile)
            sheet.write(i, 18, '1,2,3,4,5,6,7,8')
            i = i + 1
