# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils
import logging

logger = logging.getLogger(__name__)

class OpStudentExtendDueDate(models.TransientModel):
    _name = "op.student.extend.due.date.wizard"
    _description = "Modify due date in admission of student"

    @api.model
    def _get_domain(self):
        student_id = self.env.context.get('active_ids', []) or []
        student = self.env['op.student'].browse(student_id).id
        return [('student_id.id', '=', str(student))]

    admission_ids = fields.Many2many(
        'op.admission',
        string='Admissions',
        required=True,
        help="Select one or more admissions",
        domain=_get_domain
    )
    months_to_extend = fields.Integer(
        string='Months',
        required=True,
        help="Number of months to extend",
        default=1
    )

    def extend(self):
        for admission in self.admission_ids:
            new_date = self.calculate_date(admission.due_date)
            admission.update({
                'due_date' : new_date,
                })
            logger.info("Update due date to admission %s" % admission.application_number)
        body = '''<p> Se ha realizado una prórroga de %s %s a los siguientes cursos:</p>
        ''' % (self.months_to_extend, 'mes' if self.months_to_extend == 1 else 'meses')
        for admission in self.admission_ids:
            body = body + '''<p> <strong>Admisión:</strong> %s </p>
            <p><strong>Curso:</strong> %s </p> 
            <p><strong>Grupo:</strong> %s </p>
            <p><strong>Fecha de Vencimiento:</strong> %s </p>
            ___________________________________
            ''' %(admission.application_number, admission.course_id.name,
                    admission.batch_id.code, admission.due_date)
        for admission in self.admission_ids:
            message = admission.student_id.message_post(body=body, subject="Prórroga" ,message_type='comment')
            admission.student_id.env['mail.mail'].create({ 'mail_message_id' : message.id,
                                                            'body_html' : body,
                                                            'notification' : True,
                                                            'recipient_ids' : [(4, admission.partner_id.id)],
                                                            'auto_delete' : True,
                                                            'references' : message.message_id,
                                                            'headers' : "'{'X-Odoo-Objects': 'op.student-1'}'"})
            mail_id = self.env['mail.mail'].search([])
            admission.student_id.env['mail.notification'].create({ 
                                                            'mail_message_id' : message.id,
                                                            'res_partner_id'  : admission.partner_id.id,
                                                            'is_read' : True,
                                                            'is_email' : True,
                                                            'mail_id' : mail_id[0].id   
                                                             })
            message.write({
                            "subtype_id": 1,
                            'needaction_partner_ids': [(4,admission.partner_id.id)],
                            'partner_ids' : [(4,admission.partner_id.id)],
                            })
            break
        # template = self.env['mail.template'].search(
        #     [('name', '=', 'Email Extend Due Date Message')])
        # template.send_mail(self.id, force_send=True,
        #                     raise_exception=True)

    def calculate_date(self, date):
        new_date = date_utils.add(date, months=self.months_to_extend)
        return new_date
