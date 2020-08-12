# -*- coding: utf-8 -*-
# © 2018 Qubiq 2010
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import logging
import unicodedata
from datetime import datetime
from dateutil import relativedelta

logger = logging.getLogger(__name__)



class crm_temp3(models.Model):
    _name = 'crm.temp3'

    name = fields.Char(string="Nombre de la iniciativa")
    codigo = fields.Char(string='Codigo de identidad')
    leadsource = fields.Char(string='Portal 1')
    source = fields.Char(string='Portal 2')
    cod_curso = fields.Char(string='Código del curso')
    cod_sede = fields.Char(string='Código de la sede')
    cod_modalidad = fields.Char(string='Código de la modalidad')
    nombre = fields.Char(string='Nombre')
    apellidos = fields.Char(string='Apellidos')
    phone = fields.Char(string='Teléfono')
    mobile = fields.Char(string='Móvil')
    email = fields.Char(string='Correo electrónico')
    pais = fields.Char(string='')
    state = fields.Char(string='Provincia')
    anno_nac = fields.Char(string='Fecha de nacimiento')
    ciudad = fields.Char(string='Ciudad')
    estudios_finalizados = fields.Char(
        string='Estudios finalizados por el contacto')
    lane = fields.Char(string='Dirección')
    terms = fields.Boolean(string='Acepta terminos')
    cp = fields.Char(string='Código Postal')
    descripcion = fields.Text(string='Descripción')
    sexo = fields.Char(string='Sexo')
    horario = fields.Char(string='Horario del contacto')
    fecha_lead = fields.Datetime(string="Fecha llegada")
    check = fields.Boolean(string="Pasado")
    other = fields.Text(string="Query")

    code = fields.Char(string="Código")
    campanya = fields.Char(string="Campaña")
    id_comercial = fields.Char(string="ID Comercial")
    cod_tipo_curso = fields.Char(string="Código tipo de curso")
    curso = fields.Char(string="Curso")
    cod_area = fields.Char(string="Código del Area")
    content = fields.Char(string="Content")
    medium = fields.Char(string="Medium")
    utma = fields.Char(string="UTMA")
    modalidad = fields.Char(string="Modalidad")
    sede = fields.Char(string="Sede")
    tipo_curso = fields.Char(string="Tipo curso")
    term = fields.Char(string="Tipo sesión")
    error_iniciativa = fields.Text(string="Motivo del error")
    check_error = fields.Boolean()

    iniciativa_id = fields.Many2one(
        "crm.lead",
        string="Iniciativa"
    )

    rel_country = {
        "Tunez": "Tunisia",
        "Suecia": "Sweden",
        "Emiratos Arabes Unidos": "United Arab Emirates",
        "Dinamarca": "Denmark",
        "Polonia": "Poland",
        "R. DOMINICANA": "Dominican Republic",
        "Timor Oriental": "East Timor",
        "Japon": "Japan",
        "TAX MEXICO": "Mexico",
        "Puerto Rico, USA": "Puerto Rico",
        "Ucrania": "Ukraine",
        "Kazajstan": "Kazakhstan",
        "Espanya": "Spain",
        "España": "Spain",
        "Espaã±a": "Spain",
        "Alemania": "Germany",
        "Brasil": "Brazil",
        "Estados Unidos": "United States",
        "Francia": "France",
        "Italia": "Italy",
        "México": "Mexico",
        "Paises": "",
        "Panamá": "Panama",
        "Perú": "Peru",
        "República Dominicana": "Dominican Republic",
        "Republica Dominicana": "Dominican Republic"
    }

    sex = {
        "Hombre": 'Hombre',
        "Home": 'Hombre',
        "Mujer": 'Mujer',
        "Dona": 'Mujer',
    }

    
    @api.multi
    def simple(self,id):
        logger.info('Lead CRON:')
        temp_lead_obj = self.env['crm.temp3'].search([('id', '=', id)], limit=100)
        for lead in temp_lead_obj:
            logger.info('INICIATIVA ENTRANTE:')
            logger.info(lead)
            #self.ajustar_lead(lead)
            self._simple3(lead)  


    @api.multi
    def _simple3(self, lead):
        cliente_obj = self.env['res.partner'].search([('email', '=', lead.email)])

        if len(cliente_obj) > 1:
            cliente_obj = cliente_obj[0]

        country_id = self.env['res.country'].search([
            ('name', '=', lead.pais),
            ('code', '!=', ''),
            ('create_uid', '!=', None)])
        logger.info(country_id)
        if country_id.id is None:
            country_id=self.env['res.company'].browse(51)

        state_id = self.env['res.country.state'].search([
            ('name', '=', lead.state),
            ('code', '!=', ''),
            ('create_uid', '!=', '')])
        logger.info(state_id)
        if lead.codigo.upper()=='ISEP':
            company_id=self.env['res.company'].browse(1)
        else:
            company_id=self.env['res.company'].browse(3)
        logger.info(company_id)
        date = datetime.now()
        if lead.curso=='Becas conecta':
            lead.descripcion ='Becas conecta'


        vals_lead = {
            'partner_id': cliente_obj.id,
            'contact_name': lead.nombre + ' ' + lead.apellidos,
            'phone': lead.phone,
            'description': lead.descripcion,
            'x_sexo': lead.sexo in self.sex and self.sex[lead.sexo] or '',
            'x_titulacion': lead.estudios_finalizados,
            'zip': lead.cp,
            'country_id': country_id.id ,
            'state_id': state_id.id ,
            'city': 'lead.ciudad',
            'x_annonacimiento': 1900,
            'email_from': lead.email,
            'street': lead.lane,
            'company_id': company_id.id,
            'name': 'Importacion Simple',
            'create_date': date,
            'x_codcurso': '',
            'x_codsede': '',
            'x_codmodalidad': lead.cod_modalidad,
            'x_codarea': lead.cod_area,
            'x_finalizacionestudios': lead.estudios_finalizados,
            'x_ga_campaign': lead.campanya,
            'x_content': lead.content,
            'x_ga_medium': lead.medium,
            'x_ga_utma': lead.utma,
            'x_ga_source': '',
            'x_modalidad_id': 0,
            'x_codtipodecurso': '',
            'user_id': 0,
            'x_sede_id': 0,
            'team_id': 0,
            'x_producto_id': 0,
            'x_area_id': 0,
            'x_curso_id': 0,
            'x_tipodecurso_id': '',
            'x_grupoduplicado': '',
            'x_numdups': 0,
            'x_precontactonuevodup': ''
            }

        lead_obj = self.env['crm.lead']
        lead.iniciativa_id = lead_obj.sudo().create(vals_lead).id

        if lead.iniciativa_id:
            lead.check = True
            lead.check_error = False
            lead.error_iniciativa = ''
        else:
            logger.info("ERROR!")
