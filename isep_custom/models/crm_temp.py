# -*- coding: utf-8 -*-
from openerp import models, fields, api
import logging
import datetime
import sys
#from importlib import reload
#reload(sys)
#sys.setdefaultencoding('UTF8')
logger = logging.getLogger(__name__)


class crm_temp(models.Model):
    _name = 'crm.temp'

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
        "Alemania": "Germany",
        "Brasil": "Brazil",
        "Estados Unidos": "United States",
        "Francia": "France",
        "Italia": "Italy",
        "México": "Mexico",
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

    # -- Función relacionada con acción automatizada -- #
    @api.multi
    def lead_cron(self):
        temp_lead_obj = self.env['crm.temp'].search(
            [('check', '=', False)], limit=5)

        for lead in temp_lead_obj:
            logger.info('INICIATIVA ENTRANTE:')
            logger.info(lead)
            self._check_lead(lead)

    # -- Función relacionada con el botón en iniciativas entrantes -- #
    @api.multi
    def validate_lead(self):
        for lead in self:
            logger.info('INICIATIVA ENTRANTE:')
            logger.info(lead)
            self._check_lead(lead)

    # -- Función para validar las iniciativas -- #
    @api.multi
    def _check_lead(self, lead):
        pais = lead.pais.encode('utf-8')

        if lead.pais.encode('utf-8') not in self.rel_country:
            country_id = self.env['res.country'].search([
                ('name', '=', lead.pais),
                ('code', '!=', ''),
                ('create_uid', '!=', '')])
        else:
            country_id = self.env['res.country'].search([
                ('name', '=', self.rel_country[pais])])

        date = datetime.datetime.now()

        # Buscar equipo de ventas según los datos entrados y  #
        # comercial encargado del mismo                       #
        # 2 casos únicos debido a irregularidades en la BBDD  #
        id_equipo_ventas = None
        if lead.sede.lower() == 'ised online':
            id_equipo_ventas = self.env['crm.team'].search([
                ('name', '=', 'ISED Barcelona')
            ])

        elif lead.sede.lower() == 'isep madrid':
            id_equipo_ventas = self.env['crm.team'].search([
                ('name', '=', 'Madrid')
            ])

        else:
            id_equipo_ventas = self.env['crm.team'].search([
                ('name', 'ilike', lead.sede)
            ])
        user_id = id_equipo_ventas.user_id
        # FIN #

        state_id = self.env['res.country.state'].search([
            ('name', '=', lead.state),
            ('code', '!=', ''),
            ('create_uid', '!=', '')])

        if len(state_id) > 1:
            state_id = state_id[0]

        if not isinstance(lead.anno_nac, int):
            nac = ''

        company_id = self.env['res.company'].search([
            ('name', '=', lead.codigo)])

        if lead.phone == '':
            lead.phone = lead.mobile

        # Escoge la modalidad del curso - Parche para coger     #
        # la modalidad correcta según el valor de la empresa    #
        # ISEP - attribute_id = 2 / ISED - attb_id = 3          #

        mod = self.env['product.attribute.value'].search([
            ('name', '=', lead.cod_modalidad)
        ])

        if len(mod) > 1:
            attb_id = None
            if company_id.name == 'ISEP':
                attb_id = 2

            elif company_id.name == 'ISED':
                attb_id = 3

            if attb_id:
                mod = self.env['product.attribute.value'].search([
                    ('name', '=', lead.cod_modalidad),
                    ('attribute_id', '=', attb_id)
                ])

        # FIN #

        # Busqueda del producto a partir del nombre del curso,  #
        # el codigo de curso y la sede.                         #
        # Los datos recogidos son unicode por lo tanto se       #
        # tienen que codificar a utf8                           #

        default_code = str(lead.cod_curso+lead.cod_sede)
        nombre_curso = lead.curso.encode('utf-8')

        if nombre_curso[-1] is ')':
            nombre_curso = nombre_curso[:-2]
            nombre_curso = nombre_curso.strip()

        logger.info(nombre_curso)
        logger.info(default_code)

        prod_id = self.env['product.product'].search([
            ('name', 'ilike', nombre_curso),
            ('default_code', '=', default_code)
        ])
        logger.info("1")
        logger.info(prod_id)

        # Parche - no todos los codigos se forman igual - BBDD  #

        if len(prod_id) < 1:
            logger.info("IF MAL: ")
            logger.info(lead.cod_curso + lead.cod_modalidad)
            prod_id = self.env['product.product'].search([
                ('name', 'ilike', nombre_curso),
                ('default_code', '=', str(
                    lead.cod_curso + lead.cod_modalidad))
            ])

            logger.info("2")
            logger.info(prod_id)

        if len(prod_id) < 1:
            logger.info("IF MAL OTRA VEZ: ")
            logger.info(str(lead.cod_curso))
            prod_id = self.env['product.product'].search([
                ('name', 'ilike', nombre_curso),
                ('default_code', 'ilike',
                    str(lead.cod_tipo_curso+lead.cod_curso))
            ])

            logger.info("3")
            logger.info(prod_id)

        if len(prod_id) < 1:
            logger.info("IF MAL OTRA OTRA VEZ: ")
            logger.info(str(lead.cod_curso))
            prod_id = self.env['product.product'].search([
                ('name', 'ilike', nombre_curso),
                ('default_code', '=', str(lead.cod_curso))
            ])

            logger.info("4")
            logger.info(prod_id)

        # FIN #

        # Busqueda de area de estudio #

        area = self.env['product.category'].search([
                ('x_codigocategoria', '=', lead.cod_area.upper()),
                ('x_compania', '=', company_id.name)
        ])

        # FIN #

        # Parche para caso especifico - error en BBDD #
        if lead.cod_tipo_curso.upper() == 'CU':
            tipocurso = self.env['x.crmtipodecurso'].search([
                ('x_codigotipodecurso', '=', 'PR'),
                ('x_name', '!=', '')
            ])

        else:
            tipocurso = self.env['x.crmtipodecurso'].search([
                ('x_codigotipodecurso', '=', lead.cod_tipo_curso.upper()),
                ('x_name', '!=', '')
            ])

        # FIN #

        curso = self.env['product.template'].search([
            ('name', 'ilike', nombre_curso),
            ('company_id', '=', company_id.id)
        ])

        if len(curso) > 1:
            curso = curso[0]

        # Busqueda del campo "Delegacion" #

        id_sede = self.env['product.attribute.value'].search([
                ('x_descripcion', 'ilike', lead.sede)
            ])

        # Lista de códigos para los tags - WIP #
        """
        lista_tags = []
        lista_tmp = []
        lista_tmp.append(self.cod_curso)
        lista_tmp.append(self.cod_tipo_curso)
        lista_tmp.append(id_equipo_ventas.id)

        for cod in lista_tmp:
            tag = self.env['crm.lead.tag'].search([
                ('name', 'ilike', cod),
                ])
            if len(tag) > 1:
                tag = tag[0]

            if tag:
                lista_tags.append(tag.id)

        tags_ids = [(6, 0, [lista_tags])]

        """

        # FIN #
        if country_id and company_id and prod_id:
            vals = {
                'contact_name': lead.nombre + ' ' + lead.apellidos,
                'phone': lead.phone,
                'description': lead.descripcion,
                'x_sexo': lead.sexo in self.sex and self.sex[lead.sexo] or '',
                'x_titulacion': lead.estudios_finalizados,
                'zip': lead.cp,
                'country_id': country_id.id,
                'state_id': state_id.id,
                'city': lead.ciudad,
                # 'x_horario_id': horario_id.id,
                'x_annonacimiento': nac,
                'email_from': lead.email,
                'street': lead.lane,
                'company_id': company_id.id,
                'name': lead.cod_curso + lead.cod_sede + ' - ' + lead.email,
                'create_date': date,
                'x_codcurso': lead.cod_curso,
                'x_codsede': lead.cod_sede,
                'x_codmodalidad': lead.cod_modalidad,
                'x_codarea': lead.cod_area,
                'x_finalizacionestudios': lead.estudios_finalizados,
                'x_ga_campaign': lead.campanya,
                'x_content': lead.content,
                'x_ga_medium': lead.leadsource,
                'x_ga_utma': lead.utma,
                'x_modalidad_id': mod.id,
                'x_codtipodecurso': lead.cod_tipo_curso,
                'user_id': user_id.id,
                'x_sede_id': id_sede.id,
                'team_id': id_equipo_ventas.id,
                'x_producto_id': prod_id.id,
                'x_area_id': area.id,
                'x_curso_id': curso.id,
                'x_tipodecurso_id': tipocurso.id,
                # 'tag_ids': tags_ids
                }

            lead_obj = self.env['crm.lead']
            lead.iniciativa_id = lead_obj.sudo().create(vals).id
            if lead.iniciativa_id:
                lead.check = True
            else:
                logger.info("ERROR!")
