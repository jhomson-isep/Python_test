# -*- coding: utf-8 -*-

import logging
# from mailchimp3 import MailChimp
from odoo import api, fields, models, _
from odoo.models import expression
from odoo.exceptions import UserError, ValidationError
from itertools import groupby
# from validate_email import validate_email
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    verificar_email = fields.Boolean(string="Mail erroneo", default=False)
    bool_mail_chimp = fields.Boolean(string="Sinc. MailChimp", default=False)
    x_universidad = fields.Char(string='Universidad')
    x_titulacion = fields.Char(string="Estudios")
    x_tipodocumento = fields.Selection([('DNI', 'DNI'), ('Pasaporte', 'Pasaporte'), ('cif', 'CIF')], "Tipo de Documento")
    x_tipodecontacto = fields.Selection([('-----', '-----'), ('Alumno', 'Alumno'),
                                ('Alumno Potencial', 'Alumno Potencial'),
                                ('Cliente', 'Cliente'),
                                ('Cliente Potencial', 'Cliente Potencial'),
                                ('Contacto', 'Contacto')],
                                string="Tipo de Contacto")
    x_sexo = fields.Selection([('Mujer', 'Mujer'), ('Hombre', 'Hombre')], string="Sexo")
    x_profesion = fields.Char(string="Profesion")
    x_oldcrmid = fields.Integer(string="Old Crm Id")
    x_finalizacionestudios = fields.Char(string="Finalización Estudios")
    birthdate = fields.Char(string="Fecha de nacimiento")
    x_aceptacondiciones = fields.Boolean(string="Acepta Condiciones")
    x_nombre = fields.Char(string="Nombre")
    x_apellidos = fields.Char(string="Apellidos")
    x_annonacimiento = fields.Integer(string="Año Nacimiento")
    x_birthdate = fields.Date(string="Fecha de Nacimiento")

    x_horarioid = fields.Many2one('x_crm.horariosdecontacto', string="Horario de Contacto")
    x_ops_ids = fields.One2many('crm.lead', 'partner_id', string='Oportunidades', domain=[('type', '=', 'opportunity'), '|', ('active', '=', True), ('active', '=', False)])
    ops_ids = fields.One2many('crm.lead', 'partner_id', string='Oportunidades', domain=[('type', '=', 'opportunity'), '|', ('active', '=', True), ('active', '=', False)])
    x_message_ids = fields.One2many('mail.message', 'res_id', string="Llamadas/Mensajes")
    #llamadas_cliente = fields.One2many(comodel_name="llamadas.isep", inverse_name="llamadas_id")

    team_id = fields.Many2one('crm.team', string="Equipo de ventas")
    email = fields.Char(index=True)
    name = fields.Char(index=True)
    vat = fields.Char(index=True)
    count_efectos = fields.Integer(string='Efectos', compute="_get_count_efectos")

    @api.multi
    def _get_count_efectos(self):
        for sel in self:
            sel.count_efectos = len(sel.env['account.move.line'].search([
                ('partner_id', '=', sel.id),
                ('account_id.internal_type', 'in', ['receivable', 'payable']),
                ('amount_residual', '>', 0.0),
                ]))

    @api.multi
    def correccion_paises(self):
        self.env.cr.execute('UPDATE res_partner SET country_id=69 WHERE country_id=254')

    @api.multi
    def unlink_states_partner(self):
        self.env.cr.execute("UPDATE res_partner SET state_id=NULL WHERE state_id is not NULL")

    """
    @api.multi
    @api.constrains('vat')
    def _check_reconcile(self):
        for sel in self:
            if sel.vat:
                partners_duplicates = None
                if sel.company_id:
                    partners_duplicates = self.env['res.partner'].search([('company_id','=',sel.company_id.id),('vat', '=', sel.vat), ('id', '!=', sel.id)])
                else:
                    partners_duplicates = self.env['res.partner'].search([('vat', '=', sel.vat), ('id', '!=', sel.id)])
                if partners_duplicates:
                    names = ''
                    for partner in partners_duplicates:
                        names += '\n' + partner.name + '. ID:' + str(partner.id)
                    raise ValueError(_('No se puede añadir el NIF debido a que está duplicado para los siguientes clientes: %s') % names)
    """

    @api.multi
    def false_bool_mail_chimp_P(self):
        for partner in self.env['res.partner'].search([
           ('bool_mail_chimp', '=', True),
           ('company_id', 'in', (19, 8, 1, 14))]):
            partner.bool_mail_chimp = False

    @api.multi
    def false_bool_mail_chimp_D(self):
        for partner in self.env['res.partner'].search([
           ('bool_mail_chimp', '=', True),
           ('company_id', 'in', (3, 7, 5, 4, 6))]):
            partner.bool_mail_chimp = False

    """
    Funcion que retorna los indices de separacion de split
    realizado para la separacion de nombre y apellidos
    """
    def splitwithindices(self, s, c=' '):
        p = 0
        for k, g in groupby(s, lambda x: x == c):
            q = p + sum(1 for i in g)
            if not k:
                yield p, q  # or p, q-1 if you are really sure you want that
            p = q

    """
    Accion automatizada para el traspaso de clientes a mailchimp
    para P, la lista de contactos es OdooP 7534e7ac0e
    """
    # @api.multi
    # def accion_automatica_mailchimp_P(self):
    #     connection = MailChimp(
    #         'qubiq_2018',
    #         'aa556aec812b4f20438474c438456ee6-us2')
    #     opciones_cursos = (
    #         'curso', 'pgrado', 'diplo',
    #         'mgrafico', 'master')
    #     add_a_mailchimp =\
    #         [x.values()[0] for x in connection.lists.members.all(
    #             '7534e7ac0e',
    #             get_all=True,
    #             fields="members.email_address")['members']]
    #     for partner in self.env['res.partner'].search([
    #         ('bool_mail_chimp', '=', False),
    #         ('verificar_email', '=', False),
    #         ('company_id', 'in', (19, 8, 1, 14)),
    #         ('child_ids', '=', False),
    #         ('email', '!=', False),
    #         ('email', '!=', ''),
    #         ('user_ids', '=', False),
    #         ('name', '!=', False),
    #         ('name', '!=', ' '),
    #         ('name', '!=', '  '),
    #        ], limit=50):
    #         if partner.email in add_a_mailchimp:
    #             for part in self.env['res.partner'].search([
    #                 ('email', '=', partner.email),
    #                 ('company_id', 'in', (19, 8, 1, 14))
    #                ]):
    #                 part.bool_mail_chimp = True
    #         else:
    #             # se realiza por aqui el control debido a que al final
    #             # se realiza un cambio para los partners con el mismo mail
    #             # y la misma companyia (para que no haga PUM)
    #             if validate_email(partner.email, verify=True):
    #                 if partner.bool_mail_chimp:
    #                     continue
    #                 _logger.info("--> contacto mailchimp")
    #                 _logger.info(partner.name)
    #                 # Separamos nombre de apellidos
    #                 nombre = ''
    #                 apellido = ''
    #                 index_split = list(self.splitwithindices(partner.name))
    #                 _logger.info(index_split)
    #                 if len(index_split) > 3:
    #                     nombre = partner.name[:index_split[1][1]]
    #                     apellido = partner.name[index_split[2][0]:]
    #                 elif len(index_split) == 1:
    #                     nombre = partner.name
    #                 else:
    #                     nombre = partner.name[:index_split[0][1]]
    #                     apellido = partner.name[index_split[1][0]:]
    #                 # Alumno, si tiene un SO y esta enviado a la acedemica lo es
    #                 # Tambien se ponen los cursos

    #                 cursos = ''
    #                 alumno = 'No'
    #                 for so in partner.sale_order_ids:
    #                     if so.x_enviado_crm:
    #                         alumno = 'Si'
    #                         for line in so:
    #                             if line.product_id.tipodecurso in opciones_cursos:
    #                                 if cursos != '':
    #                                     cursos += ', ' + line.product_id.name
    #                                 else:
    #                                     cursos = line.product_id.name
    #                 # Se rellenan los campos de las oportunidades
    #                 source = ''
    #                 medium = ''
    #                 campaign = ''
    #                 area = ''
    #                 if partner.x_ops_ids:
    #                     source = partner.x_ops_ids[0].x_ga_source or ''
    #                     medium = partner.x_ops_ids[0].x_ga_medium or ''
    #                     campaign = partner.x_ops_ids[0].x_ga_campaign or ''
    #                     area = partner.x_ops_ids[0].x_codarea or ''
    #                 try:
    #                     res = connection.lists.members.create(
    #                         list_id='7534e7ac0e',
    #                         data={
    #                             "email_address": partner.email,
    #                             "status": "subscribed",
    #                             "merge_fields": {
    #                                 "FNAME": nombre or '',  # nombre
    #                                 "LNAME": apellido or '',  # apellido
    #                                 "CREATEDTIM": partner.create_date or '',
    #                                 "CIUDAD": partner.city or '',
    #                                 "ESTADO": partner.state_id.name or '',
    #                                 "PAIS": partner.country_id.name or '',
    #                                 "CODIGO_POS": partner.zip or '',
    #                                 "TEL_MOVIL": partner.mobile or '',
    #                                 "TEL_FIJO": partner.phone or '',
    #                                 "ALUMNO": alumno,
    #                                 "SEDE": partner.company_id.name or '',
    #                                 "SOURCE": source,
    #                                 "MEDIUM": medium,
    #                                 "CAMPAIGN": campaign,
    #                                 "AREA": area,
    #                                 "CURSO": cursos,
    #                                 },
    #                             })
    #                     # Se ponen como enviados todos los clientes
    #                     # con ese mismo mail para que no se repitan y de error
    #                     for part in self.env['res.partner'].search([
    #                         ('email', '=', partner.email),
    #                         ('company_id', 'in', (19, 8, 1, 14))
    #                        ]):
    #                         part.bool_mail_chimp = True
    #                 except ValueError:
    #                     _logger.info("ERROR - MAILCHIMP accion_automatica_mailchimp_P, user: " + str(partner.id))
    #             else:
    #                 for part in self.env['res.partner'].search([
    #                     ('email', '=', partner.email),
    #                     ('company_id', 'in', (19, 8, 1, 14))
    #                    ]):
    #                     part.verificar_email = True
    #             _logger.info(res)

    """
    Accion automatizada para el traspaso de clientes a mailchimp
    para D, la lista de contactos es OdooD 40655eb16d
    """
    # @api.multi
    # def accion_automatica_mailchimp_D(self):
    #     connection = MailChimp(
    #         'qubiq_2018',
    #         'aa556aec812b4f20438474c438456ee6-us2')
    #     opciones_cursos = (
    #         'curso', 'pgrado', 'diplo',
    #         'mgrafico', 'master')
    #     add_a_mailchimp =\
    #         [x.values()[0] for x in connection.lists.members.all(
    #             '40655eb16d',
    #             get_all=True,
    #             fields="members.email_address")['members']]
    #     for partner in self.env['res.partner'].search([
    #         ('bool_mail_chimp', '=', False),
    #         ('verificar_email', '=', False),
    #         ('company_id', 'in', (3, 7, 5, 4, 6)),
    #         ('child_ids', '=', False),
    #         ('email', '!=', False),
    #         ('email', '!=', ''),
    #         ('user_ids', '=', False),
    #         ('name', '!=', False),
    #         ('name', '!=', ' '),
    #         ('name', '!=', '  '),
    #        ], limit=50):
    #         if partner.email in add_a_mailchimp:
    #             for part in self.env['res.partner'].search([
    #                     ('email', '=', partner.email),
    #                     ('company_id', 'in', (3, 7, 5, 4, 6))
    #                     ]):
    #                 part.bool_mail_chimp = True
    #         else:
    #             if validate_email(partner.email, verify=True):
    #                 # se realiza por aqui el control debido a que al final
    #                 # se realiza un cambio para los partners con el mismo mail
    #                 # y la misma companyia (para que no haga PUM)
    #                 if partner.bool_mail_chimp:
    #                     continue
    #                 _logger.info("--> contacto mailchimp")
    #                 _logger.info(partner.name)
    #                 # Separamos nombre de apellidos
    #                 nombre = ''
    #                 apellido = ''
    #                 index_split = list(self.splitwithindices(partner.name))
    #                 _logger.info(index_split)
    #                 if len(index_split) > 3:
    #                     nombre = partner.name[:index_split[1][1]]
    #                     apellido = partner.name[index_split[2][0]:]
    #                 elif len(index_split) == 1:
    #                     nombre = partner.name
    #                 else:
    #                     nombre = partner.name[:index_split[0][1]]
    #                     apellido = partner.name[index_split[1][0]:]
    #                 # Alumno, si tiene un SO y esta enviado a la acedemica lo es
    #                 # Tambien se ponen los cursos

    #                 cursos = ''
    #                 alumno = 'No'
    #                 for so in partner.sale_order_ids:
    #                     if so.x_enviado_crm:
    #                         alumno = 'Si'
    #                         for line in so:
    #                             if line.product_id.tipodecurso in opciones_cursos:
    #                                 if cursos != '':
    #                                     cursos += ', ' + line.product_id.name
    #                                 else:
    #                                     cursos = line.product_id.name
    #                 # Se rellenan los campos de las oportunidades
    #                 source = ''
    #                 medium = ''
    #                 campaign = ''
    #                 area = ''
    #                 if partner.x_ops_ids:
    #                     source = partner.x_ops_ids[0].x_ga_source or ''
    #                     medium = partner.x_ops_ids[0].x_ga_medium or ''
    #                     campaign = partner.x_ops_ids[0].x_ga_campaign or ''
    #                     area = partner.x_ops_ids[0].x_codarea or ''
    #                 try:
    #                     res = connection.lists.members.create(
    #                         list_id='40655eb16d',
    #                         data={
    #                             "email_address": partner.email,
    #                             "status": "subscribed",
    #                             "merge_fields": {
    #                                 "FNAME": nombre or '',  # nombre
    #                                 "LNAME": apellido or '',  # apellido
    #                                 "CREATEDTIM": partner.create_date or '',
    #                                 "CIUDAD": partner.city or '',
    #                                 "ESTADO": partner.state_id.name or '',
    #                                 "PAIS": partner.country_id.name or '',
    #                                 "CODIGO_POS": partner.zip or '',
    #                                 "TEL_MOVIL": partner.mobile or '',
    #                                 "TEL_FIJO": partner.phone or '',
    #                                 "ALUMNO": alumno,
    #                                 "SEDE": partner.company_id.name or '',
    #                                 "SOURCE": source,
    #                                 "MEDIUM": medium,
    #                                 "CAMPAIGN": campaign,
    #                                 "AREA": area,
    #                                 "CURSO": cursos,
    #                                 },
    #                             })
    #                     # Se ponen como enviados todos los clientes
    #                     # con ese mismo mail para que no se repitan y de error
    #                     for part in self.env['res.partner'].search([
    #                         ('email', '=', partner.email),
    #                         ('company_id', 'in', (3, 7, 5, 4, 6))
    #                        ]):
    #                         part.bool_mail_chimp = True
    #                 except ValueError:
    #                     _logger.info("ERROR - MAILCHIMP accion_automatica_mailchimp_D, user: " + str(partner.id))
    #             else:
    #                 for part in self.env['res.partner'].search([
    #                     ('email', '=', partner.email),
    #                     ('company_id', 'in', (19, 8, 1, 14))
    #                    ]):
    #                     part.verificar_email = True
    #             _logger.info(res)
