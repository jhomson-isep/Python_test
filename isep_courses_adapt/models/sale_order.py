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
        res = super(SaleOrder, self).action_confirm()
        return res

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

    def get_sale_order_in_admission(self):
        exists = False
        so_id = self.env['op.admission'].search(
            [('sale_order_id', '=', self.id)], limit=1).id
        if so_id:
            exists = True
        logger.info("sale order: {}".format(so_id))
        return exists

    def send_educat(self, batch_id):
        is_student = False
        register_id = self.get_register_id(batch_id)
        student_id = self.get_student_id()

        people = 'CON:' + str(self.partner_id.id)

        if student_id:
            is_student = True
            people = 'ALU:' + str(student_id)

        split_name = self.partner_id.name.split()
        middle = ''
        if len(split_name) > 2:
            first, middle, last = filter(lambda x: x not in ('M', 'Shk', 'BS'),
                                         self.partner_id.name.split())
        else:
            first, last = filter(lambda x: x not in ('M', 'Shk', 'BS'),
                                 self.partner_id.name.split())

        admission_values = {
            'street': self.partner_id.street, 'zip': self.partner_id.zip,
            'city': self.partner_id.city, 'sale_order_id': self.id,
            'name': self.partner_id.name,
            'batch_id': batch_id.id,
            'email': self.partner_id.email,
            'last_name': last,
            'first_name': first,
            'middle_name': middle,
            'country_id': self.partner_id.country_id.id,
            'state_id': self.partner_id.state_id.id,
            'application_date': datetime.datetime.today(),
            'birth_date': self.partner_id.x_birthdate,
            'gender': self.get_gender(),
            'register_id': register_id,
            'course_id': batch_id.course_id.id,
            'application_number': str(
                batch_id.id) + '-' + people,
            'is_student': is_student, 'student_id': student_id,
            'partner_id': self.partner_id.id
        }
        if admission_values:
            exists = self.get_sale_order_in_admission()
            if exists:
                raise UserError(_("Student already in admission"))
            else:
                if register_id is None or register_id is False:
                    raise UserError(_("Student without admission"))
                new_obj = self.env['op.admission'].create(admission_values)
                logger.info("params:{}".format(admission_values))

    @api.multi
    def action_send_student(self):
        self.ensure_one()
        if not self.partner_id.x_sexo or not self.partner_id.x_birthdate:
            raise UserError(_('Fields sex and birthday are required'))

        if not self.in_admission:
            for line in self.order_line:
                course_type = line.product_id.tipodecurso
                logger.info('Line ========> {}'.format(line))
                logger.info('Course type =======> {}'.format(course_type))
                if course_type in ['curso', 'pgrado', 'diplo', 'mgrafico',
                                   'master']:
                    self.send_educat(line.batch_id)
                else:
                    logger.info(course_type)
            self.in_admission = True
        return {}
