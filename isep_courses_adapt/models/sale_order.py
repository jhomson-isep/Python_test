# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models, fields, api, _
import datetime
import logging

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    in_admission = fields.Boolean(string="In admission", default=False)

    @api.multi
    def action_confirm(self):
        for order in self:
            order.action_send_student()
        return super(SaleOrder, self).action_confirm()

    def get_register_id(self, batch_id):
        admission_register_id = self.env['op.admission.register'].search(
            [('batch_id', '=', batch_id.id)], limit=1).id
        return admission_register_id or None

    def get_student_id(self):
        student_id = self.env['op.student'].search(
            [('partner_id', '=', self.partner_id.id)], limit=1).id
        return student_id or None

    def get_gender(self):
        gender = False
        if self.partner_id.x_sexo == 'Mujer':
            gender = 'f'
        elif self.partner_id.x_sexo == 'Hombre':
            gender = 'm'
        return gender or 'o'

    def get_sale_order_in_admission(self, application_number):
        admission_count = self.env['op.admission'].search_count(
            [('application_number', '=', application_number)])
        return admission_count > 0

    def send_student(self, batch_id):
        register_id = self.get_register_id(batch_id)
        student_id = self.get_student_id()
        is_student = student_id is not None
        people = ':'.join(['CON', str(self.partner_id.id)])

        first_name, middle_name, last_name, last_name2 = self.split_names(
            self.partner_id.name)

        admission_last_name = last_name
        if last_name2 not in last_name and last_name2 != '':
            admission_last_name = ' '.join([last_name, last_name2])

        application_number = str(batch_id.id) + '-' + people
        admission_values = {
            'street': self.partner_id.street, 'zip': self.partner_id.zip,
            'city': self.partner_id.city, 'sale_order_id': self.id,
            'name': self.partner_id.name,
            'batch_id': batch_id.id,
            'email': self.partner_id.email,
            'last_name': admission_last_name,
            'first_name': first_name,
            'middle_name': middle_name,
            'country_id': self.partner_id.country_id.id,
            'state_id': self.partner_id.state_id.id,
            'application_date': datetime.datetime.today(),
            'birth_date': self.partner_id.x_birthdate,
            'gender': self.get_gender(),
            'register_id': register_id,
            'course_id': batch_id.course_id.id,
            'application_number': application_number,
            'is_student': is_student, 'student_id': student_id,
            'partner_id': self.partner_id.id,
            'phone': self.partner_id.phone,
            'mobile': self.partner_id.mobile or self.partner_id.phone
        }
        if admission_values:
            exists = self.get_sale_order_in_admission(application_number)
            if self.state == 'sale':
                if exists:
                    raise UserError(_("Estudiante ya enviado a admisión"))
                if register_id is None or register_id is False:
                    raise UserError(_("Registro de admisión no encontrado, "
                                      "contacte a su administrador de "
                                      "sistemas"))
            if not exists:
                admission = self.env['op.admission'].create(admission_values)
                logger.info("params:{}".format(admission_values))
                logger.info("Admission created: {}".format(admission))

    @api.multi
    def action_send_student(self):
        self.ensure_one()
        if not self.partner_id.x_sexo or not self.partner_id.x_birthdate:
            raise UserError(_('Los campos Seco y Fecha de nacimiento son '
                              'requeridos'))

        for line in self.order_line:
            course_type = line.product_id.tipodecurso
            logger.info('Line ========> {}'.format(line))
            logger.info('Course type =======> {}'.format(course_type))
            if course_type in ['curso', 'pgrado', 'diplo', 'mgrafico',
                               'master']:
                if not line.batch_id.id and self.company_id.id in [1, 1111]:
                    raise UserError(_(
                        'El grupo es obligatorio para el producto: {}'.format(
                            line.product_id.name)))

                if line.batch_id.id:
                    self.send_student(line.batch_id)
            else:
                logger.info(course_type)

        return {}

    @staticmethod
    def split_names(name):
        u"""
        It separates the first and last names and returns a tuple of three
        elements (string) formatted for names with the first character
        capitalized. This is assuming that in the chain the names and
        surnames are ordered in the ideal way:

        1- name or names.
        2- first surname.
        3- second surname.

        split_names( '' )
        ('Name', 'Middle name', 'Last name')
        """

        # Separate the full name into spaces.
        tokens = name.split(" ")

        # List with words of the name.
        names_list = []

        # Words of surnames and compound names.
        special_tokens = ['da', 'de', 'di', 'do', 'del', 'la', 'las',
                          'le', 'los', 'mac', 'mc', 'van', 'von', 'y', 'i',
                          'san', 'santa']

        prev = ""
        for token in tokens:
            _token = token.lower()

            if _token in special_tokens:
                prev += token + " "

            else:
                names_list.append(prev + token)
                prev = ""

        len_names = len(names_list)
        names, middle_name, last_name, last_second_name = "", "", "", ""

        # When there is no name.
        if len_names == 0:
            names = ""

        # When the name consists of a single element.
        elif len_names == 1:
            names = names_list[0]

        # When the name consists of two elements.
        elif len_names == 2:
            names = names_list[0]
            last_name = names_list[1]

        # When the name consists of three elements.
        elif len_names == 3:
            names = names_list[0]
            last_name = names_list[1]
            last_second_name = names_list[2]

        # When the name consists of more than three elements.
        else:
            names = names_list[0]
            middle_name = names_list[1]
            last_name = names_list[2] + " " + names_list[3]
            last_second_name = names_list[3]

        # We set the strings with the first character in uppercase.
        names = names.title()
        last_name = last_name.title()
        last_second_name = last_second_name.title()
        middle_name = middle_name.title()

        return names, middle_name, last_name, last_second_name

    # def update_sale_order(self):
    #     so=self.env['sale.order'].search([('id','=',7)])
    #     values7={
    #         'precio_primer_pago' : 1900,
    #         'precio_matricula' : 4300
    #     }
    #     p23=self.env['res.partner'].search([('id','=',23)])
    #     values_ptk={
    #         'partner_id':23,
    #         'acquirer_id':2,
    #         'acquirer_ref':1234567899998765
    #     }
    #
    #     pt=self.env['payment.token'].create(values_ptk)
    #     values23={
    #         'payment_token_ids':[pt]
    #     }
    #     p23.write(values23)
    #     so.write(values7)

