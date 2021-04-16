from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
import logging
import xlwt
from xlsxwriter.workbook import Workbook
import base64
import io
import pandas as pd

logger = logging.getLogger(__name__)

#Se define el modelo (clase) para el Wizard.
#TransientModel indica que se trata de un modelo (clase models) en el cual sus datos permaneceran
#durante un tiempo en el sistema Odoo, luego se eliminaran automaticamente.

class OpApvWizard(models.TransientModel):
    #Se define el nombre y descripcion del modulo en el sistema Odoo
    _name = "op.apv.wizard"
    _description = "Wizard de Admisiones y pedidos de ventas"
    _inherit = 'report.report_xlsx.abstract'

    #Se definen los campos (fields) que indican lo que el modelo puede guardar y donde.
    date_init = fields.Date(string="Desde", required=True)
    date_end = fields.Date(string="Hasta", required=True)
    course_id = fields.Many2one("op.course", string="Course ID")
    batch = fields.Many2one("op.batch", string="batchs")
    sale_order_ids = fields.Many2one("op.student", string="IDs_sales_orders")
    admision_register = fields.Many2one("op.admission.register", string="Adm_regs")

    #Funcion de ejemplo, self hace referencia al objeto del tipo 'op.admisiones.pedidos.de.venta.wizard'
    def testfunction(self):
        print('Exito!')

    #Se definen funciones relacionadas
    def test_wizard(self):
        print("Inicio del Wizard")
        #Se ejecuta una funcion perteneciente al objeto 'op.admisiones.pedidos.de.venta.wizard'.
        self.testfunction()
        #self es un objeto del tipo 'op.admisiones.pedidos.de.venta.wizard' y contiene todas sus funciones
        #y atributos.
        #Se procede a filtrar todas las admisiones segun un parametro o condicion determinada, en este caso
        #se filtra entre un rango de fechas.
        #Se hace llamado al modelo op.admission quien contiene todas las admisiones, cada modelo tiene una
        #funcion 'search' que permite filtrar datos a partir de unas condiciones dadas.
        #Se hace la busqueda exacta del curso que tenga un id igual al id seleccionado que sera guardado en
        #self.course_id.id, este ultimo es exactamente el id del curso seleccionado.
        admissions = self.env['op.admission'].search([('application_date', '>' , self.date_init),
                                                      ('application_date', '<' , self.date_end),
                                                      ('course_id', '=' , self.course_id.id)])
        #Una vez adquirido todos los admission ID de todas las admisiones relacionadas con el curso
        #seleccionado, se procede a imprimir cada una de ellas con un ciclo for.
        for admission in admissions:
            print('Admission ID:'+str(admission.id))
            print('Nombre:'+str(admission.first_name))
            print('Fecha de admisión:'+str(admission.admission_date))
            print('Codigo:'+str(admission.application_number))

    def generate_xlsx_apv_report(self, workbook):
        admissions = self.env['op.admission'].search([('application_date', '>' , self.date_init),
                                                      ('application_date', '<' , self.date_end),
                                                      ('course_id', '=' , self.course_id.id)])

        df = pd.DataFrame({'': ['']})
        f = io.BytesIO()
        
        writer = pd.ExcelWriter(f, engine='xlsxwriter')

        df.to_excel(writer, sheet_name='APV')

        workbook  = writer.book
        worksheet = writer.sheets['APV']

        #Titulos del reporte:
        worksheet.write(1,0,"ID")
        worksheet.write(1,1,"Primer nombre")
        worksheet.write(1,2,"Estudiante/Matricula")
        worksheet.write(1,3,"Fecha de admisión")
        worksheet.write(1,4,"Grupo/Curso/Nombre")
        worksheet.write(1,5,"Sale order id/ID")
        worksheet.write(1,6,"Sale order id/Nombre a mostrar")
        worksheet.write(1,7,"Sale order id/Comercial/Nombre")
        worksheet.write(1,8,"Sale order id/Base imponible")
        worksheet.write(1,9,"Sale order id/Comercial/Correo electronico")
        worksheet.write(1,10,"Grupo/Curso/Modalidad")
        worksheet.write(1,11,"Grupo/Sede/Name")
        worksheet.write(1,12,"Estado")
        worksheet.write(1,13,"Fecha de baja")
        worksheet.write(1,14,"Sale order id/Compañia/Nombre de la compañia")

        #Se formatean las celdas necesarias para dar una forma adecuada al reporte.
        format_a = workbook.add_format({'fg_color': '#ffffff'})
        format_b = workbook.add_format({'num_format': '#,##0.00'})
        worksheet.conditional_format('A2:O2', {'fg_color': '#D7E4BC'})
        
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 30)
        worksheet.set_column('I:I', 30)
        worksheet.set_column('J:J', 45)
        worksheet.set_column('K:K', 30)
        worksheet.set_column('L:L', 30)
        worksheet.set_column('M:M', 20)
        worksheet.set_column('N:N', 30)
        worksheet.set_column('O:O', 50)

        #Apuntador para recorrer las filas
        i = 2

        for obj in admissions:

            worksheet.write(i,0,obj.id)
            worksheet.write(i,1,obj.first_name)
            worksheet.write(i,2,obj.student_id.gr_no)
            worksheet.write(i,3,obj.admission_date)
            worksheet.write(i,4,obj.course_id.name)

            #Datos de sales
            worksheet.write(i,5,obj.sale_order_id.id)
            worksheet.write(i,6,obj.sale_order_id.display_name)
            worksheet.write(i,7,obj.sale_order_id.user_id.name)
            worksheet.write(i,8,obj.sale_order_id.amount_untaxed)
            worksheet.write(i,9,obj.sale_order_id.user_id.email)

            worksheet.write(i,10,obj.batch_id.code)
            worksheet.write(i,11,obj.sale_order_id.team_id.name)
            worksheet.write(i,12,obj.state)
            worksheet.write(i,13,obj.unsubscribed_date)
            worksheet.write(i,14,obj.sale_order_id.company_id.name)

            i+=1
    
        writer.save()

        xlsx_data = f.getvalue()

        file_gtf = base64.b64encode(xlsx_data)
        attachment = self.env['ir.attachment'].create({
            'name': 'Test_xlsx.xlsx',
            'type': 'binary',
            'datas': file_gtf,
            'datas_fname': 'Test_xlsx.xlsx',
            'res_model': 'op.admission',
            'res_id': '1',
            'mimetype': "application/vnd. ms-excel"
            })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{0}?download=true'.format(attachment.id),
            'target': 'new',
            'nodestroy': False,
            }