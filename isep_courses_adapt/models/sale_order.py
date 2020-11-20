# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
import datetime
import logging
import csv

import traceback

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_register_id(self, code):
        register_id = self.env['op.admission.register'].search(
            [('batch_id.code', '=', code)], limit=1).id
        return register_id or None

    def get_student_id(self):
        student_id = self.env['op.student'].search(
            [('partner_id', '=', self.partner_id.id)], limit=1).id
        return student_id or None

    def get_gender(self):
        if self.partner_id.x_sexo == 'Mujer':
            sexo = 'f'
        if self.partner_id.x_sexo == 'Hombre':
            sexo = 'm'
        return sexo

    def send_educat(self, id, line):
        register_id = self.get_register_id(line.preferred_batch_id.code)
        student_id = self.get_student_id()

        people = 'CON:' + str(self.partner_id.id)

        if student_id:
            is_student = True
            people = 'ALU:' + str(student_id)

        _params = {
            'street': self.partner_id.street, 'zip': self.partner_id.zip,
            'city': self.partner_id.city, 'sale_order_id': self.id,
            'name': self.partner_id.name,
            'batch_id': line.preferred_batch_id.id,
            'email': self.partner_id.email,
            'last_name': self.partner_id.x_apellidos or self.partner_id.name,
            # not null
            'middle_name': self.partner_id.x_nombre,
            'country_id': self.partner_id.country_id.id,
            'state_id': self.partner_id.state_id.id,
            'application_date': datetime.datetime.today(),
            'birth_date': self.partner_id.x_birthdate,
            'gender': self.transform_sex(),
            'register_id': register_id,
            'course_id': line.preferred_batch_id.course_id.id,
            'application_number': str(
                line.preferred_batch_id.id) + '-' + people,
            'is_student': is_student, 'student_id': student_id,
            'partner_id': self.partner_id.id
        }
        if _params:
            exists = self.get_sale_order_in_admission()
            if exists:
                raise UserError(_("Student in admission"))
            # controlar el register_id
            # agregar el wizar pero controlar lo anterior
            else:
                if register_id is None or register_id is False:
                    raise UserError(_("Student without admission"))
                new_obj = self.env['op.admission'].create(_params)
                logger.info("params:{}".format(_params))
