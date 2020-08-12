# -*- coding: utf-8 -*-
# © 2018 Qubiq 2010
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import logging
import unicodedata
from datetime import datetime
from dateutil import relativedelta

logger = logging.getLogger(__name__)



class crm_temp2(models.Model):
    _name = 'crm.temp2'

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

    def _dict_company(self):
        res = {}
        for company in self.env['res.company'].sudo().search([]):
            res[company.name.lower()] = company.id
        return res

    # -- Función relacionada con acción automatizada -- #
    @api.multi
    def lead_cron(self):
        logger.info('Lead CRON:')
        temp_lead_obj = self.env['crm.temp2'].search([
            ('check', '=', False), ('check_error', '=', False)], limit=100)
        for lead in temp_lead_obj:
            logger.info('INICIATIVA ENTRANTE:')
            logger.info(lead)
            self.ajustar_lead(lead)
            #self._check_lead(lead)
            self._traspasar_lead(lead)

    @api.multi
    def traspasar_uno(self,id):
        logger.info('Lead CRON:')
        temp_lead_obj = self.env['crm.temp2'].search([('id', '=', id)], limit=100)
        for lead in temp_lead_obj:
            logger.info('INICIATIVA ENTRANTE:')
            logger.info(lead)
            self.ajustar_lead(lead)
            self._traspasar_lead(lead)

    @api.multi
    def simple_uno(self,id):
        logger.info('Lead CRON:')
        temp_lead_obj = self.env['crm.temp2'].search([('id', '=', id)], limit=100)
        for lead in temp_lead_obj:
            logger.info('INICIATIVA ENTRANTE:')
            logger.info(lead)
            self.ajustar_lead(lead)
            self._simple_base(lead)

    @api.multi
    def cron_simple(self):
        logger.info('Lead CRON:')
        temp_lead_obj = self.env['crm.temp2'].search([('check', '=', False), ('check_error', '=', False), ('id','>',200000000)], limit=100)
        for lead in temp_lead_obj:
            logger.info('INICIATIVA ENTRANTE:')
            logger.info(lead)
            self.ajustar_lead(lead)
            self._simple_base(lead)
    # -- Función relacionada con el botón en iniciativas entrantes -- #
    @api.multi
    def validate_lead(self):
        for lead in self:
            self.ajustar_lead(lead)
            logger.info('INICIATIVA ENTRANTE:')
            logger.info(lead)
            self._check_lead(lead)

    # -- Función relacionada con el botón en iniciativas entrantes -- #
    @api.multi
    def traspasar_lead(self):
        for lead in self:
            self.ajustar_lead(lead)
            logger.info('INICIATIVA ENTRANTE:')
            logger.info(lead)
            self._traspasar_lead(lead)
    # -- Función relacionada con el botón en iniciativas entrantes -- #
    @api.multi
    def simple_lead(self):
        for lead in self:
            self.ajustar_lead(lead)
            self.mayusculas_lead(lead)
            logger.info('INICIATIVA ENTRANTE:')
            logger.info(lead)
            self._simple_lead(lead)


    # -- Función relacionada con el botón en iniciativas entrantes -- #
    @api.multi
    def total_lead(self):
        for lead in self:
            self.ajustar_lead(lead)
            logger.info('INICIATIVA ENTRANTE:')
            logger.info(lead)
            self._check_lead(lead)
            if lead.iniciativa_id == 0:
                self._traspasar_lead(lead)
            if lead.iniciativa_id == 0:
                self._simple_lead(lead)

    # -- Función relacionada con el botón en iniciativas entrantes -- #
    @api.multi
    def cerrar_lead(self):
        for lead in self:
            lead.check = True
                

    # -- Función relacionada con el botón en iniciativas entrantes -- #
    @api.multi
    def ajustar_lead(self,lead):
        lead.phone = lead.phone.replace(" ", "") 
        lead.phone = lead.phone.replace(".", "") 
        lead.phone = lead.phone.replace("-", "") 
        lead.mobile = lead.mobile.replace(" ","")
        lead.mobile = lead.mobile.replace(".","")
        lead.mobile = lead.mobile.replace("-","")
        lead.email = lead.email.replace(" ", "") 
        lead.email = lead.email.lower() 
        #lead.nombre =  lead.nombre.upper()
        lead.nombre = lead.nombre.replace("  ", " ") 
        #lead.apellidos = lead.apellidos.upper()
        lead.apellidos = lead.apellidos.replace("  ", " ") 
        lead.codigo = lead.codigo.upper()
    @api.multi
    def mayusculas_lead(self,lead):
        lead.nombre =  lead.nombre.upper()
        lead.apellidos = lead.apellidos.upper()
        lead.codigo = lead.codigo.upper()


    # -- Función para validar las iniciativas -- #
    @api.multi
    def _check_lead(self, lead):
        try:
            pais = lead.pais.encode('utf-8')
            logger.info("**************************** ")
            logger.info(lead.codigo)
            logger.info(lead.cod_sede)
            if lead.pais=='Espaã±a':
                lead.pais='España'

            if lead.codigo == 'ISEP' and lead.cod_sede=='MAD':
                logger.info("CAMIANDO  MADRID")
                lead.cod_sede='MDR'
                sede_llamada = 'MDR'
            if lead.codigo == 'ISTN':
                lead.cod_sede='IST'
            if lead.cod_sede=='AH!':
                lead.cod_sede='CAT'
                lead.descripcion = "Método at Home"

            if lead.pais != '-':
                if lead.pais != 'Otro':
                    llamada_pais = False
                    if lead.pais.encode('utf-8') not in self.rel_country:
                        logger.info("----------1-----------")
                        country_id = self.env['res.country'].search([
                            ('name', '=', lead.pais),
                            ('code', '!=', ''),
                            ('create_uid', '!=', None)])
                    else:
                        logger.info("----------2-----------")
                        country_id = self.env['res.country'].search([
                            ('name', '=', self.rel_country[pais])])

                    if not country_id:
                        logger.info("----------3-----------")
                        country_id = self.env['res.country'].search([
                            ('code', 'ilike', lead.pais),
                            ('create_uid', '!=', None)])

                    if not country_id:
                        logger.info("----------4-----------")
                        country_id = self.env['res.country'].search([
                            ('name', 'ilike', lead.pais),
                            ('create_uid', '!=', None),
                            ])
                else:
                    llamada_pais = True
                    country_id = self.env['res.country'].search([
                        ('code', '=', 'vacio')
                    ])

            else:
                if lead.phone[:2] == '52':
                    country_id = self.env['res.country'].search([
                        ('code', '=', 'MX'),
                        ('create_uid', '!=', None)])
                elif lead.phone[:2] == '57':
                    country_id = self.env['res.country'].search([
                        ('code', '=', 'CO'),
                        ('create_uid', '!=', None)])

                else:
                    llamada_pais = True
                    country_id = self.env['res.country'].search([
                        ('code', '=', 'vacio')
                    ])

            date = datetime.now()

            state_id = self.env['res.country.state'].search([
                ('name', '=', lead.state),
                ('code', '!=', ''),
                ('create_uid', '!=', '')])

            if len(state_id) > 1:
                state_id = state_id[0]

            if not isinstance(lead.anno_nac, int):
                nac = ''

            # Buscar equipo de ventas según los datos entrados y  #
            # comercial encargado del mismo                       #
            # 2 casos únicos debido a irregularidades en la BBDD  #

            id_equipo_ventas = None
            if lead.cod_sede != '-':
                logger.info("NO HAY -")
                if lead.cod_sede != ' ':
                    logger.info("TENGO COD SEDE: %s", lead.cod_sede)

                    if country_id.code in ['CO', 'MX'] and lead.cod_modalidad != 'PRS':
                        id_equipo_ventas = self.env['crm.team'].search([
                                ('code', '=', 'MEX')
                            ])

                    elif lead.cod_sede == 'INT':
                        logger.info("ENTRO EN EL INT")
                        id_equipo_ventas = self.env['crm.team'].search([
                            ('code', '=', 'BCN')
                        ])

                    else:
                        if lead.cod_sede == 'ONL':
                            if lead.codigo == 'ISED':
                                id_equipo_ventas = self.env['crm.team'].search([
                                        ('code', '=', 'BCN')
                                    ])

                            if lead.codigo == 'ISEP':
                                id_equipo_ventas = self.env['crm.team'].search([
                                        ('code', '=', 'ONL')
                                    ])
                        else:
                            id_equipo_ventas = self.env['crm.team'].search([
                                        ('code', '=', lead.cod_sede)
                                    ])
                else:
                    logger.info("NO TENGO COD SEDE")
                    if country_id.code in ['CO', 'MX'] and lead.cod_modalidad != 'PRS':
                        id_equipo_ventas = self.env['crm.team'].search([
                                ('code', '=', 'MEX')
                            ])

                    else:
                        if lead.sede.lower() == 'sesiones clínicas online':
                            id_equipo_ventas = self.env['crm.team'].browse(5)

                        elif lead.sede.lower() == 'sesiones clínicas valencia':
                            id_equipo_ventas = self.env['crm.team'].browse(2)

                        elif lead.sede.lower() == 'sesiones clínicas barcelona':
                            id_equipo_ventas = self.env['crm.team'].browse(1)

                        elif lead.sede.lower() == 'sesiones clínicas barcelona':
                            id_equipo_ventas = self.env['crm.team'].browse(4)

                        elif lead.sede.lower() == 'isep madrid' or lead.sede.lower() == 'madrid' and lead.codigo == 'ISEP':
                            id_equipo_ventas = self.env['crm.team'].browse(4)

                        elif lead.sede.lower() == 'isep valencia' or lead.sede.lower() == 'valencia' and lead.codigo == 'ISEP':
                            id_equipo_ventas = self.env['crm.team'].browse(2)

                        elif lead.cod_modalidad == 'PRS':
                            if lead.codigo == 'ISED':
                                id_equipo_ventas = self.env['crm.team'].search([
                                        ('code', '=', 'BCN')
                                    ])
                            if lead.codigo == 'ISEP':
                                id_equipo_ventas = self.env['crm.team'].search([
                                        ('code', '=', 'CAT')
                                    ])

                        else:
                            id_equipo_ventas = self.env['crm.team'].search([
                                            ('name', 'ilike', lead.sede),
                                            ('code', '!=', None)
                                        ])

                        if len(id_equipo_ventas) > 1:
                            id_equipo_ventas = self.env['crm.team'].search([
                                        ('name', 'ilike', lead.sede),
                                        ('name', 'ilike', lead.codigo),
                                        ('code', '!=', None)
                                    ])
            if lead.codigo == 'ISTN':
                id_equipo_ventas= self.env['crm.team'].browse(26)

            logger.info("EQUIPO DE VENTAS: %s", id_equipo_ventas)

            company_id = id_equipo_ventas.company_id
            user_id = id_equipo_ventas.user_id

            # FIN #
            if lead.phone == '':
                lead.phone = lead.mobile

            # Busqueda del producto a partir del nombre del curso,  #
            # el codigo de curso y la sede.                         #
            # Los datos recogidos son unicode por lo tanto se       #
            # tienen que codificar a utf8                           #

            default_code = str(lead.cod_curso+lead.cod_sede)
            nombre_curso = lead.curso.encode('utf-8')
            check_tipo = False
            prod_id = False

            tipocurso = lead.tipo_curso.encode('utf-8')
            if tipocurso == 'Máster':
                tipocurso = 'Master'

            if tipocurso == 'Posgrado':
                tipocurso = 'Pgrado'

            if tipocurso == 'Monográfico':
                tipocurso = 'Mgrafico'

            if nombre_curso:
                if nombre_curso[-1] is ')':
                    nombre_curso = nombre_curso[:-2]
                    nombre_curso = nombre_curso.strip()

            # Corrección de nombres de curso #

                if nombre_curso == 'Máster de patologías del lenguaje y el habla':
                    nombre_curso = 'Máster en patologías del lenguaje y el habla'

                if nombre_curso == 'Máster en logopedia clínica en daño neurológico':
                    nombre_curso = 'Máster de logopedia clínica en daño neurológico'

            # FIN #

            logger.info("Codigos de curso y modalidad")
            logger.info("Curso: %s", lead.cod_curso)
            logger.info("Modalidad: %s", lead.cod_modalidad)
            logger.info("Compañía: %s", company_id.name)

            if lead.cod_curso != '' and lead.cod_curso != '-':
                logger.info("Con codigo de curso")
                                        
                prod_code = self.env['product.product'].search([
                    ('default_code', '=', lead.cod_curso+lead.cod_modalidad)
                ])
                compania=0
                if lead.codigo == 'ISED':
                    compania=3
                else:
                    compania=1
                if lead.codigo == 'ISTN':
                    compania=4

                prod_code_compania = self.env['product.product'].search([
                    ('default_code', '=', lead.cod_curso+lead.cod_modalidad),
                    ('company_id', '=', compania)
                ])

                prod_code_compania_base = self.env['product.product'].search([
                    ('default_code', '=', lead.cod_curso)
                ])
                logger.info("Compañia: %s", company_id.id)
                logger.info("Compañia: %s", compania)
                logger.info("curso+mod: %s", prod_code)
                logger.info("Compañia: %s", prod_code_compania)
                logger.info("Compañia Base: %s", prod_code_compania_base)
                logger.info("Tipo de Curso: %s", tipocurso)


                if tipocurso != ' ' and tipocurso != '':
                    logger.info("ENTRO EN EL NUEVO IF DEL DATO")
                    logger.info("prod_code: %s", prod_code)
                    if prod_code:
                        if len(prod_code) > 1:
                            logger.info("campo 1: %s", prod_code)
                            for course in prod_code:
                                if tipocurso in course.tipodecurso.capitalize():
                                    check_tipo = True
                                    prod_code = course
                        else:
                            logger.info("Comprobación: %s != %s", tipocurso.capitalize(), prod_code.tipodecurso.capitalize())
                            logger.info(tipocurso)
                            logger.info(prod_code.tipodecurso)
                            if tipocurso != prod_code.tipodecurso.capitalize():
                                prod_code = False
                            else:
                                check_tipo = True

                        if check_tipo is False:
                            prod_code = False

                logger.info("Producto: %s", prod_code)
                logger.info("Producto Compañia: %s", prod_code_compania)


                if not prod_code:
                    prod_code = self.env['product.product'].search([
                        ('default_code', '=', lead.cod_curso)
                    ])

                if len(prod_code) < 1:
                    prod_code = self.env['product.product'].search([
                        ('default_code', '=', lead.cod_curso+lead.cod_sede) 
                    ])

                logger.info("Producto Antes: %s", prod_code)
                if len(prod_code) > 1:
                    for product in prod_code:
                        if company_id in product.company_ids:
                            logger.info("ENTRO EN IF-FOR 1")
                            prod_id = product

                else:
                    for product in prod_code:
                        if company_id in product.company_ids:
                            logger.info("ENTRO EN IF-FOR 2")
                            prod_id = product
                            logger.info("Producto Antes: %s", prod_id)
                        else:
                            logger.info (" HAY QUE CALCULAR DE NUEVO")
                            prod_code = self.env['product.product'].search([('default_code', '=', lead.cod_curso)])
                            if len(prod_code) > 1:
                                for product in prod_code:
                                    if company_id in product.company_ids:
                                        logger.info("ENTRO EN EL SEGUNDO IF-FOR")
                                        prod_id = product
                            else:
                                prod_id = prod_code
            logger.info("Siguente paso: %s", prod_id)

            if not prod_id:
                logger.info("Sin código de curso")
                logger.info("Nombre curso: %s", nombre_curso)
                logger.info("Tipo variable: %s", type(nombre_curso))

                prod_id = self.env['product.product'].search([
                    ('name_template', 'ilike', nombre_curso),
                    ('default_code', '!=', '-')
                ])

                logger.info("Lista 1: %s", prod_id)

                if len(prod_id) > 1:
                    for product in prod_id:
                        logger.info("ENTRO EN FOR")
                        if company_id in product.company_ids:
                            logger.info("ENTRO EN IF-FOR")
                            prod_id = product

                logger.info("Lista 2: %s", prod_id)
            logger.info("Siguente paso 2: %s", prod_id)

            # Referencia interna mal formada

            #if nombre_curso == 'Auxiliar de clínica dental':
            #    prod_id = self.env['product.product'].search([
            #        ('default_code', '=', lead.cod_tipo_curso+lead.cod_curso)
            #    ])

            # FIN

            # Busqueda de area de estudio #

            if lead.cod_area != '-':
                area = self.env['product.category'].search([
                        ('x_codigocategoria', '=', lead.cod_area.upper()),
                        ('x_compania', 'ilike', company_id.name)
                ])

                if len(area) > 1:
                    area = area[0]
            else:
                area = prod_id.categ_id

            # FIN #

            curso = prod_id.product_tmpl_id

            mod_final = self.env['product.attribute.value'].search([
                ('name', '=', lead.cod_modalidad)
            ])

            if lead.cod_sede == 'INT':
                mod_final = self.env['product.attribute.value'].search([
                    ('name', '=', lead.cod_modalidad),
                    ('attribute_id', '=', 2)
                ])

            if len(mod_final) > 1:
                if company_id.id in (1, 19):
                    mod_final = self.env['product.attribute.value'].search([
                        ('name', '=', lead.cod_modalidad),
                        ('attribute_id', '=', 2)
                    ])
                else:
                    mod_final = self.env['product.attribute.value'].search([
                        ('name', '=', lead.cod_modalidad),
                        ('attribute_id', '=', 3)
                    ])

            if len(mod_final) < 1:
                if company_id.id == 1:
                    mod_final = self.env['product.attribute.value'].search([
                        ('name', '=', lead.cod_modalidad),
                        ('attribute_id', '=', 2)
                    ])
                else:
                    mod_final = self.env['product.attribute.value'].search([
                        ('name', '=', lead.cod_modalidad),
                        ('attribute_id', '=', 3)
                    ])

            # Busqueda del campo "Delegacion" #
            id_sede = self.env['product.attribute.value']
            if lead.cod_sede == '-':
                id_sede = self.env['product.attribute.value']

            elif lead.cod_sede == 'INT':
                id_sede = self.env['product.attribute.value'].search([
                    ('x_descripcion', '=', 'ISEP Internacional')
                ])

            else:
                if lead.cod_sede == ' ' and lead.sede.lower() == 'sesiones clínicas valencia':
                    id_sede = self.env['product.attribute.value'].browse(5)
                    lead.medium = 'sesión clínica'
                if lead.cod_sede == ' ' and lead.sede.lower() == 'sesiones clínicas barcelona':
                    id_sede = self.env['product.attribute.value'].browse(2)
                    lead.medium = 'sesión clínica'
                if lead.cod_sede == ' ' and lead.sede.lower() == 'sesiones clínicas madrid':
                    id_sede = self.env['product.attribute.value'].browse(3)
                    lead.medium = 'sesión clínica'
                if lead.cod_sede == ' ' and lead.sede.lower() == 'sesiones clínicas online':
                    id_sede = self.env['product.attribute.value'].browse(26)
                    lead.medium = 'sesión clínica'
                elif lead.cod_sede != ' ' and lead.cod_sede != '-':
                    id_sede = self.env['product.attribute.value'].search([
                            ('name', '=', lead.cod_sede)
                        ])

                    if len(id_sede) > 1:
                        if company_id.id == 1:
                            id_sede = self.env['product.attribute.value'].search([
                                ('name', '=', lead.cod_sede),
                                ('attribute_id', '=', 1)
                            ])
                        else:
                            id_sede = self.env['product.attribute.value'].search([
                                ('name', '=', lead.cod_sede),
                                ('attribute_id', '=', 4)
                            ])
                else:
                    if lead.codigo == 'ISEP':
                        if lead.sede.lower() == 'isep madrid' or lead.sede.lower() == 'madrid':
                            id_sede = self.env['product.attribute.value'].search([
                                    ('x_descripcion', '=', 'campus Madrid')
                                ])
                        if lead.sede.lower() == 'barcelona':
                            id_sede = self.env['product.attribute.value'].search([
                                    ('name', '=', 'CAT')
                                ])

            if len(id_sede) != 1:
                id_sede = self.env['product.attribute.value'].search([
                                ('x_descripcion', 'ilike', lead.sede),
                            ])

            # Duplicidad de Iniciativas #

            numdups = 0
            precontacto = 'Única'
            grupoduplicado = 0
            lista_dup = []
            company_string = ''

            # if lead.codigo != 'ISED':
            dup_lead_obj = self.env['crm.lead'].search([
                ('|'),
                ('phone', '=', lead.phone),
                ('email_from', 'ilike', lead.email),
                ('active', '=', True),
                ('type', '=', 'lead')])

            if dup_lead_obj is None:
                dup_lead_obj = self.env['crm.lead'].search([
                ('|'),
                ('phone', 'ilike', lead.phone[:9]),
                ('email_from', 'ilike', lead.email),
                ('active', '=', True),
                ('type', '=', 'lead')])
            logger.info("Siguente paso ANTES DE: %s", prod_id)


            if dup_lead_obj:
                for dup in dup_lead_obj:
                    logger.info("Lead duplicado: %s", dup.name)
                    if dup.company_id.id not in lista_dup:
                        lista_dup.append(dup.company_id.id)
                        company_string = \
                            company_string + ', '
                        company_string = \
                            company_string + str(dup.company_id.name)

                    if dup.x_grupoduplicado != 0:
                        grupoduplicado = dup.x_grupoduplicado
                    else:
                        sql_crm_dup = \
                            "select nextval('crm_lead_x_grupoduplicado_seq') as valor"
                        self._cr.execute(sql_crm_dup)
                        res = self._cr.fetchall()
                        grupoduplicado = res[0]
                        grupoduplicado = grupoduplicado[0]

                    if dup.x_precontactonuevodup == 'Única':
                        sql_crm_dup = \
                            "select nextval('crm_lead_x_grupoduplicado_seq') as valor"
                        self._cr.execute(sql_crm_dup)
                        res = self._cr.fetchall()
                        leadduplicado = res[0]
                        leadduplicado = leadduplicado[0]

                        if len(lista_dup) > 1:
                            precontacto = "Duplicada (%s)%s" % \
                                (leadduplicado, company_string)
                        else:
                            precontacto = "Duplicada(%s)" % (leadduplicado)

                        dup.write({'x_precontactonuevodup': precontacto})

                numdups = len(dup_lead_obj)

                if len(lista_dup) > 1:
                    precontacto = "Duplicada (%s)%s" % \
                        (grupoduplicado, company_string)
                else:
                    precontacto = "Duplicada(%s)" % (grupoduplicado)

            # FIN #

            # Duplicidad de Contactos #
            contactonuevodup = "Nuevo"

            partner_dup = self.env['res.partner'].search([
                ('|'),
                ('|'),
                ('phone', '=', lead.phone),
                ('mobile', '=', lead.phone),
                ('email', 'ilike', lead.email)],
                limit=1)
            if partner_dup is None:
                logger.info("NO LO Encuentra y lo busca")
                partner_dup = self.env['res.partner'].search([
                    ('|'),
                    ('phone', '=', lead.phone[:9]),
                    ('email', 'ilike', lead.email)],
                    limit=1)
            logger.info("Partner duplicado: %s", partner_dup.name)

            if partner_dup.user_id:
                contactonuevodup = partner_dup.user_id.name

            # Rellenar posibles códigos que faltan #

            # Código de sede #
            if lead.cod_sede == ' ':
                if id_equipo_ventas.id == 22:
                    sede_llamada = 'MDR'
                else:
                    sede_llamada = id_equipo_ventas.code
            else:
                sede_llamada = lead.cod_sede

            # Código de tipo de curso #
            curso_init = ''

            if lead.cod_tipo_curso == ' ' and prod_id.tipodecurso != ' ':
                if prod_id.tipodecurso == 'master':
                    curso_init = 'MT'
                elif prod_id.tipodecurso == 'curso':
                    curso_init = 'CU'
                elif prod_id.tipodecurso == 'pgrado':
                    curso_init = 'CU'
            elif prod_id.tipodecurso == '':
                logger.info("Entro en el elif")
                curso_init = ''
            else:
                logger.info("Entro en el else")
                curso_init = lead.cod_tipo_curso
            # FIN #

            # Código de curso #
            if lead.cod_curso == ' ' or lead.cod_curso == '-':
                codigo_producto = prod_id.default_code
                codigo_producto = codigo_producto[:2]
            else:
                codigo_producto = lead.cod_curso

            # FIN #

            logger.info("Curso init: %s", curso_init)
            logger.info("codigo_producto: %s", codigo_producto)

            # Parche para caso especifico - error en BBDD #
            if curso_init == 'CU':
                tipocurso_id = self.env['x.crmtipodecurso'].search([
                    ('x_codigotipodecurso', '=', 'PR'),
                    ('x_name', '!=', '')
                ])

            else:
                tipocurso_id = self.env['x.crmtipodecurso'].search([
                    ('x_codigotipodecurso', '=', curso_init),
                    ('x_name', '!=', '')
                ])
            logger.info("Tipo de Curso: %s", tipocurso_id)
            logger.info("Equipo de Ventas: %s", id_equipo_ventas)
            logger.info("Siguente paso 10: %s", prod_id)

            # FIN #

            # Generar nombre de iniciativa #

            if id_equipo_ventas.id == 22:
                nombre_sede = 'MDR'
            else:
                nombre_sede = id_equipo_ventas.code

            if lead.codigo == 'ISTN':
                nombre_sede = ''
                id_equipo_ventas= self.env['crm.team'].browse(26)

            logger.info("Nombre Sede: %s", nombre_sede)
            logger.info("lead email: %s", lead.email)
            try:
                lead_name = prod_id.default_code[:2] + nombre_sede + ' - ' + lead.email
            except:
                lead_name = codigo_producto+nombre_sede + ' - ' + lead.email

            


            if lead.codigo == 'ISTN':
                lead_name = 'ISTENAC - '+ lead_name

            logger.info("lead_name: %s", lead_name)
                

            # FIN #

            # Caso de las llamadas internacionales #
            logger.info("FUERA IF INT")
            if lead.curso.lower() == 'protegido: llamada internacional':
                id_equipo_ventas = self.env['crm.team'].search([
                    ('code', '=', 'BCN')
                ])
                id_sede = self.env['product.attribute.value'].search([
                    ('name', '=', 'BCN')
                ])
                logger.info("DENTRO IF INT")

                user_id = self.env['res.users'].browse(45)

            # FIN #

            cliente_obj = self.env['res.partner'].search([
                ('email', '=', lead.email)
            ])

            if len(cliente_obj) > 1:
                cliente_obj = cliente_obj[0]

            if not cliente_obj:
                # logger.info("ENTRO AQUI Y ENSEÑO INFO")
                # logger.info(lead.nombre.capitalize() + ' ' + lead.apellidos.capitalize())
                # logger.info(lead.phone)
                # logger.info(lead.email)
                # logger.info(company_id.id)
                # logger.info(id_equipo_ventas.id)
                # logger.info(user_id.id)
                vals_partner = {
                    'name': lead.nombre.capitalize() + ' ' + lead.apellidos.capitalize(),
                    'phone': lead.phone,
                    'email': lead.email,
                    'company_id': company_id.id,
                    'team_id': id_equipo_ventas.id,
                    'user_id': user_id.id,
                }
                partner_obj = self.env['res.partner']
                cliente_obj = partner_obj.sudo().create(vals_partner)

            # FIN #
            prot_prod = False
            if nombre_curso:
                prot = nombre_curso.split()
            if lead.source == 'Offiline':
                source = 'Offline'
            else:
                source = lead.leadsource

            # Si Portal 1 está vacio, coge valor de Portal 2 #
            if lead.leadsource == '':
                source = lead.source
            # FIN #

            if source == '-' and lead.leadsource != '-':
                source = lead.leadsource

            if nombre_curso:
                prot = nombre_curso.split()
                logger.info('Prot: %s', prot[0])
                if prot[0] == 'Protegido:' or prot[0] == 'Llamada':
                    logger.info("ENTRO AQUI")
                    prot_prod = True

            logger.info("IFNO:")
            logger.info(country_id)
            logger.info(id_sede)
            logger.info(company_id)
            logger.info("VALORES: %s y %s", prod_id, prot_prod)
            if prod_id or prot_prod:
                logger.info("UNO")
                if country_id or llamada_pais:
                    logger.info("DOS")
                    logger.info('ID SEDE: %s', id_sede)
                    logger.info('COMPANY ID: %s', company_id)
                    logger.info('curso_init ID: %s', curso_init)
                    logger.info('tipocurso_id : %s', tipocurso_id)
                    try:
                        eltipodecurso = tipocurso_id.id
                        logger.info('tipocurso_id.id : %s', tipocurso_id.id)
                        if lead.curso=='Becas conecta':
                            lead.descripcion ='Becas conecta'
                    except:
                        eltipodecurso = 31

                    if id_sede and company_id:
                        logger.info("TRES")
                        vals_lead = {
                            'partner_id': cliente_obj.id,
                            'contact_name': lead.nombre + ' ' + lead.apellidos,
                            'phone': lead.phone,
                            'description': lead.descripcion,
                            'x_sexo': lead.sexo in self.sex and self.sex[lead.sexo] or '',
                            'x_titulacion': lead.estudios_finalizados,
                            'zip': lead.cp,
                            'country_id': country_id.id or '',
                            'state_id': state_id.id,
                            'city': lead.ciudad,
                            'x_annonacimiento': nac,
                            'email_from': lead.email,
                            'street': lead.lane,
                            'company_id': company_id.id,
                            'name': lead_name,
                            'create_date': date,
                            'x_codcurso': codigo_producto,
                            'x_codsede': sede_llamada,
                            'x_codmodalidad': lead.cod_modalidad,
                            'x_codarea': lead.cod_area,
                            'x_finalizacionestudios': lead.estudios_finalizados,
                            'x_ga_campaign': lead.campanya,
                            'x_content': lead.content,
                            'x_ga_medium': lead.medium,
                            'x_ga_utma': lead.utma,
                            'x_ga_source': source,
                            'x_modalidad_id': mod_final.id,
                            'x_codtipodecurso': curso_init,
                            'user_id': user_id.id,
                            'x_sede_id': id_sede.id,
                            'team_id': id_equipo_ventas.id,
                            'x_producto_id': prod_id.id,
                            'x_area_id': area.id,
                            'x_curso_id': curso.id,
                            'x_tipodecurso_id': eltipodecurso,
                            'x_grupoduplicado': grupoduplicado,
                            'x_numdups': numdups,
                            'x_precontactonuevodup': precontacto
                            }

                        lead_obj = self.env['crm.lead']
                        lead.iniciativa_id = lead_obj.sudo().create(vals_lead).id

                        if lead.iniciativa_id:
                            lead.check = True
                            lead.check_error = False
                            lead.error_iniciativa = ''
                        else:
                            logger.info("ERROR!")
            else:
                lead.check_error = True
                if not id_sede:
                    lead.error_iniciativa = \
                        'No se ha encontrado una delegación valida. \n\
    ¿El código de sede es correcto?'
                if not prod_id:
                    lead.error_iniciativa = \
                        'El curso no se ha encontrado, posible error en codigo de \
                        curso, sede o modalidad. \n\
    ¿El curso existe?'
                elif not country_id:
                    lead.error_iniciativa = \
                        'El país no está o no es valido'
                elif not company_id:
                    lead.error_iniciativa = \
                        'No hay compañia seleccionada'
                elif prod_id and len(prod_id) > 1:
                    lead.error_iniciativa = \
                        'Ha encontrado mas de un resultado para el curso seleccionado, revisar códigos de curso.'
                logger.info("Error en iniciativa:")
                logger.info(lead)

        except Exception as e:
            logger.info("Error ^^************")
            logger.info(e)
            lead.check_error = True

    # -- Función para validar las iniciativas -- #
    @api.multi
    def _traspasar_lead(self, lead):
        try:
            pais = lead.pais.encode('utf-8')
            logger.info("**************************** ")
            logger.info(lead.codigo)
            logger.info(lead.cod_sede)

            if lead.codigo == 'ISEP' and lead.cod_sede=='MAD':
                logger.info("CAMIANDO  MADRID")
                lead.cod_sede='MDR'
            if lead.codigo == 'ISTN':
                lead.cod_sede='IST'
            if lead.cod_sede=='AH!':
                lead.cod_sede='CAT'
                lead.descripcion = "Método at Home"
            if lead.pais != '-':
                if lead.pais != 'Otro':
                    llamada_pais = False
                    if lead.pais.encode('utf-8') not in self.rel_country:
                        logger.info("----------1-----------")
                        country_id = self.env['res.country'].search([
                            ('name', '=', lead.pais),
                            ('code', '!=', ''),
                            ('create_uid', '!=', None)])
                    else:
                        logger.info("----------2-----------")
                        country_id = self.env['res.country'].search([
                            ('name', '=', self.rel_country[pais])])

                    if not country_id:
                        logger.info("----------3-----------")
                        country_id = self.env['res.country'].search([
                            ('code', 'ilike', lead.pais),
                            ('create_uid', '!=', None)])

                    if not country_id:
                        logger.info("----------4-----------")
                        country_id = self.env['res.country'].search([
                            ('name', 'ilike', lead.pais),
                            ('create_uid', '!=', None),
                            ])
                else:
                    llamada_pais = True
                    country_id = self.env['res.country'].search([
                        ('code', '=', 'vacio')
                    ])

            else:
                if lead.phone[:2] == '52':
                    country_id = self.env['res.country'].search([
                        ('code', '=', 'MX'),
                        ('create_uid', '!=', None)])
                elif lead.phone[:2] == '57':
                    country_id = self.env['res.country'].search([
                        ('code', '=', 'CO'),
                        ('create_uid', '!=', None)])

                else:
                    llamada_pais = True
                    country_id = self.env['res.country'].search([
                        ('code', '=', 'vacio')
                    ])

            date = datetime.now()

            state_id = self.env['res.country.state'].search([
                ('name', '=', lead.state),
                ('code', '!=', ''),
                ('create_uid', '!=', '')])

            if len(state_id) > 1:
                state_id = state_id[0]

            if not isinstance(lead.anno_nac, int):
                nac = ''

            # Buscar equipo de ventas según los datos entrados y  #
            # comercial encargado del mismo                       #
            # 2 casos únicos debido a irregularidades en la BBDD  #

            id_equipo_ventas = None
            if lead.cod_sede != '-':
                logger.info("NO HAY -")
                if lead.cod_sede != ' ':
                    logger.info("TENGO COD SEDE: %s", lead.cod_sede)

                    if country_id.code in ['CO', 'MX'] and lead.cod_modalidad != 'PRS':
                        logger.info("Caso 1")
                        id_equipo_ventas = self.env['crm.team'].search([('name', 'ilike','Mexico')], limit =1 )

                    elif lead.cod_sede == 'INT':
                        logger.info("ENTRO EN EL INT")
                        id_equipo_ventas = self.env['crm.team'].search([
                            ('name', 'ilike', 'Barcelona')
                        ])

                    else:
                        logger.info("Caso 2")
                        if lead.cod_sede == 'ONL':
                            logger.info("Caso 3")
                            if lead.codigo == 'ISED':
                                id_equipo_ventas = self.env['crm.team'].search([
                                        ('name', 'ilike', 'Barcelona')
                                    ])
                            logger.info("Caso 4")
                            if lead.codigo == 'ISEP':
                                id_equipo_ventas = self.env['crm.team'].search([
                                        ('name', 'ilike', 'Online')
                                    ])
                        else:
                            logger.info("Caso 5")
                            id_equipo_ventas = self.env['crm.team'].search([
                                        ('id', '=', 7)
                                    ],limit=1)
                else:
                    logger.info("NO TENGO COD SEDE")
                    if country_id.code in ['CO', 'MX'] and lead.cod_modalidad != 'PRS':
                        id_equipo_ventas = self.env['crm.team'].search([
                                ('name', 'ilike', 'Mexico')
                            ])

                    else:
                        if lead.sede.lower() == 'sesiones clínicas online':
                            id_equipo_ventas = self.env['crm.team'].browse(5)

                        elif lead.sede.lower() == 'sesiones clínicas valencia':
                            id_equipo_ventas = self.env['crm.team'].browse(19)

                        elif lead.sede.lower() == 'sesiones clínicas barcelona':
                            id_equipo_ventas = self.env['crm.team'].browse(1)

                        elif lead.sede.lower() == 'sesiones clínicas barcelona':
                            id_equipo_ventas = self.env['crm.team'].browse(4)

                        elif lead.sede.lower() == 'isep madrid' or lead.sede.lower() == 'madrid' and lead.codigo == 'ISEP':
                            id_equipo_ventas = self.env['crm.team'].browse(4)

                        elif lead.sede.lower() == 'isep valencia' or lead.sede.lower() == 'valencia' and lead.codigo == 'ISEP':
                            id_equipo_ventas = self.env['crm.team'].browse(19)

                        elif lead.cod_modalidad == 'PRS':
                            if lead.codigo == 'ISED':
                                id_equipo_ventas = self.env['crm.team'].search([
                                        ('name', 'ilike', 'Barcelona')
                                    ],limit=1)
                            if lead.codigo == 'ISEP':
                                id_equipo_ventas = self.env['crm.team'].search([
                                        ('id', '=', '1')
                                    ],limit=1)

                        else:
                            id_equipo_ventas = self.env['crm.team'].search([
                                            ('name', 'ilike', lead.sede)
                                        ],limit=1)

                        if len(id_equipo_ventas) > 1:
                            id_equipo_ventas = self.env['crm.team'].search([
                                        ('name', 'ilike', lead.sede),
                                        ('name', 'ilike', lead.codigo)
                                    ],limit=1)
            if lead.codigo == 'ISTN':
                id_equipo_ventas= self.env['crm.team'].browse(26)

            logger.info("EQUIPO DE VENTAS: %s", id_equipo_ventas)
            try:
                company_id = id_equipo_ventas.company_id
            except:
                logger.info("Compañia")
                company_id=self.env['res.company'].search([('id', '=', 1)])
            try:
                user_id = id_equipo_ventas.user_id
            except:
                logger.info("USUARIO")
                user_id = self.env['res.users'].browse(1)

            logger.info("Usuario: %s", user_id)
            logger.info("Compañia : %s", company_id)
            logger.info("EQUIPO DE VENTAS: %s", id_equipo_ventas)

            # FIN #
            logger.info("Empezamos con moviles")
            if lead.phone == '':
                lead.phone = lead.mobile

            # Busqueda del producto a partir del nombre del curso,  #
            # el codigo de curso y la sede.                         #
            # Los datos recogidos son unicode por lo tanto se       #
            # tienen que codificar a utf8                           #

            
            try:
                default_code = str(lead.cod_curso+lead.cod_sede)               
            except:
                default_code = 'CUSED'

            nombre_curso = lead.curso.encode('utf-8')
            check_tipo = False
            prod_id = False
            logger.info("Terminamos con mobiles")

            tipocurso = lead.tipo_curso.encode('utf-8')
            if tipocurso == 'Máster':
                tipocurso = 'Master'

            if tipocurso == 'Posgrado':
                tipocurso = 'Pgrado'

            if tipocurso == 'Monográfico':
                tipocurso = 'Mgrafico'

            if nombre_curso:
                if nombre_curso[-1] is ')':
                    nombre_curso = nombre_curso[:-2]
                    nombre_curso = nombre_curso.strip()

            # Corrección de nombres de curso #

                if nombre_curso == 'Máster de patologías del lenguaje y el habla':
                    nombre_curso = 'Máster en patologías del lenguaje y el habla'

                if nombre_curso == 'Máster en logopedia clínica en daño neurológico':
                    nombre_curso = 'Máster de logopedia clínica en daño neurológico'

            # FIN #

            logger.info("Codigos de curso y modalidad")
            logger.info("Curso: %s", lead.cod_curso)
            logger.info("Modalidad: %s", lead.cod_modalidad)
            #logger.info("Compañía: %s", company_id.name)
            logger.info("Codigos de curso y modalidad")

            if lead.cod_curso != '' and lead.cod_curso != '-':
                logger.info("Con codigo de curso")
                                        
                prod_code = self.env['product.product'].search([
                    ('default_code', '=', lead.cod_curso+lead.cod_modalidad)
                ])
                compania=0
                if lead.codigo == 'ISED':
                    compania=3
                else:
                    compania=1
                if lead.codigo == 'ISTN':
                    compania=4

                prod_code_compania = self.env['product.product'].search([
                    ('default_code', '=', lead.cod_curso+lead.cod_modalidad),
                    ('company_id', '=', compania)
                ],limit=1)

                prod_code_compania_base = self.env['product.product'].search([
                    ('default_code', '=', lead.cod_curso)
                ],limit=1)
                logger.info("Compañia: %s", company_id.id)
                logger.info("Compañia: %s", compania)
                logger.info("curso+mod: %s", prod_code)
                logger.info("Compañia: %s", prod_code_compania)
                logger.info("Compañia Base: %s", prod_code_compania_base)
                logger.info("Tipo de Curso: %s", tipocurso)


                if tipocurso != ' ' and tipocurso != '':
                    logger.info("ENTRO EN EL NUEVO IF")
                    logger.info("prod_code: %s", prod_code)
                    if prod_code:
                        if len(prod_code) > 1:
                            logger.info("campo 1: %s", prod_code)
                            logger.info("campo 1: %s", prod_code[0])
                            for course in prod_code:
                                logger.info("campo 2: %s", prod_code)
                                logger.info("campo 2: %s", course)
                        else:
                            logger.info("Comprobación: %s != %s", tipocurso.capitalize(), prod_code.tipodecurso.capitalize())
                            logger.info(tipocurso)
                            logger.info(prod_code.tipodecurso)
                            if tipocurso != prod_code.tipodecurso.capitalize():
                                prod_code = False
                            else:
                                check_tipo = True

                logger.info("Producto: %s", prod_code)
                logger.info("Producto Compañia: %s", prod_code_compania)


                if not( prod_code):
                    logger.info("No deberia Pasar por aqui: %s", prod_code)
                    prod_code = self.env['product.product'].search([
                        ('default_code', '=', lead.cod_curso)
                    ])

                if len(prod_code) < 1:
                    logger.info("No deberia Pasar por aqui 2: %s", prod_code)
                    prod_code = self.env['product.product'].search([
                        ('default_code', '=', lead.cod_curso+lead.cod_sede)
                    ])
                logger.info("Producto Antes: %s", prod_code)

                if len(prod_code) > 1:
                    logger.info("Pasamos al Producto: %s", prod_code)
                    for product in prod_code:
                        logger.info("Pasamos al Producto: %s", product)
                        if company_id == product.product_tmpl_id.company_id:
                            logger.info("ENTRO EN IF-FOR 1")
                            prod_id = product

                else:
                    for product in prod_code:
                        if company_id in product.company_ids:
                            logger.info("ENTRO EN IF-FOR 2")
                            prod_id = product
                            logger.info("Producto Antes: %s", prod_id)
                        else:
                            logger.info (" HAY QUE CALCULAR DE NUEVO")
                            prod_code = self.env['product.product'].search([('default_code', '=', lead.cod_curso)])
                            if len(prod_code) > 1:
                                for product in prod_code:
                                    if company_id in product.company_ids:
                                        logger.info("ENTRO EN EL SEGUNDO IF-FOR")
                                        prod_id = product
                            else:
                                prod_id = prod_code
            logger.info("Siguente paso: %s", prod_id)

            if not prod_id:
                logger.info("Sin código de curso")
                logger.info("Nombre curso: %s", nombre_curso)
                logger.info("Tipo variable: %s", type(nombre_curso))

                prod_id = self.env['product.product'].search([
                    ('name_template', 'ilike', nombre_curso),
                    ('default_code', '!=', '-')
                ],limit=1)

                logger.info("Lista 1: %s", prod_id)

                if len(prod_id) > 1:
                    for product in prod_id:
                        logger.info("ENTRO EN FOR")
                        if company_id in product.company_ids:
                            logger.info("ENTRO EN IF-FOR")
                            prod_id = product

                logger.info("Lista 2: %s", prod_id)

            # Referencia interna mal formada
            logger.info("Referencia Interna Mal Formada")
            logger.info(nombre_curso)
            logger.info("Seguimos")

            #try:
            #   if nombre_curso == 'Auxiliar de clínica dental':
            #        try:
            #           prod_id = self.env['product.product'].search([
            #            ('default_code', '=', lead.cod_tipo_curso+lead.cod_curso)
            #           ])
            #        except:
            #           logger.info("FIN Referencia Interna Mal Formada")
            #except:
            #       prod_id = self.env['product.product'].search(588)
            
            #logger.info("FIN Referencia Interna Mal Formada")

            # FIN

            # Busqueda de area de estudio #

            if lead.cod_area != '-':
                area = self.env['product.category'].search([
                        ('x_codigocategoria', '=', lead.cod_area.upper()),
                        ('x_compania', 'ilike', company_id.name)
                ],limit=1)

                if len(area) > 1:
                    area = area[0]
            else:
                area = self.env['product.category'].browse(1)

            # FIN #

            curso = prod_id.product_tmpl_id

            mod_final = self.env['product.attribute.value'].search([
                ('name', '=', lead.cod_modalidad)
            ],limit=1)

            if lead.cod_sede == 'INT':
                mod_final = self.env['product.attribute.value'].search([
                    ('name', '=', lead.cod_modalidad),
                    ('attribute_id', '=', 2)
                ],limit=1)

            if len(mod_final) > 1:
                if company_id.id in (1, 19):
                    mod_final = self.env['product.attribute.value'].search([
                        ('name', '=', lead.cod_modalidad),
                        ('attribute_id', '=', 2)
                    ],limit=1)
                else:
                    mod_final = self.env['product.attribute.value'].search([
                        ('name', '=', lead.cod_modalidad),
                        ('attribute_id', '=', 3)
                    ],limit=1)

            if len(mod_final) < 1:
                if company_id.id == 1:
                    mod_final = self.env['product.attribute.value'].search([
                        ('name', '=', lead.cod_modalidad),
                        ('attribute_id', '=', 2)
                    ],limit=1)
                else:
                    mod_final = self.env['product.attribute.value'].search([
                        ('name', '=', lead.cod_modalidad),
                        ('attribute_id', '=', 3)
                    ],limit=1)

            # Busqueda del campo "Delegacion" #

            id_sede = self.env['product.attribute.value']
            logger.info("Buscando Sede")
            logger.info(id_sede)
            logger.info(lead.cod_sede)
            if lead.cod_sede == '-':
                logger.info("SIN SEDE")
                id_sede = self.env['product.attribute.value']

            elif lead.cod_sede == 'INT':
                logger.info("INTERNACINAL")
                id_sede = self.env['product.attribute.value'].search([
                    ('x_descripcion', '=', 'ISEP Internacional')
                ],limit=1)

            else:
                logger.info("OTROS ")
                if lead.cod_sede == ' ' and lead.sede.lower() == 'sesiones clínicas valencia':
                    id_sede = self.env['product.attribute.value'].browse(5)
                    lead.medium = 'sesión clínica'
                if lead.cod_sede == ' ' and lead.sede.lower() == 'sesiones clínicas barcelona':
                    id_sede = self.env['product.attribute.value'].browse(2)
                    lead.medium = 'sesión clínica'
                if lead.cod_sede == ' ' and lead.sede.lower() == 'sesiones clínicas madrid':
                    id_sede = self.env['product.attribute.value'].browse(3)
                    lead.medium = 'sesión clínica'
                if lead.cod_sede == ' ' and lead.sede.lower() == 'sesiones clínicas online':
                    id_sede = self.env['product.attribute.value'].browse(26)
                    lead.medium = 'sesión clínica'
                elif lead.cod_sede != ' ' and lead.cod_sede != '-':
                    logger.info("NO HA ENCONTRADO NADA")
                    id_sede = self.env['product.attribute.value'].search([
                            ('name', '=', 'CAT')
                        ],limit=1)

                    if len(id_sede) > 1:
                        if company_id.id == 1:
                            id_sede = self.env['product.attribute.value'].search([
                                ('name', '=', lead.cod_sede),
                                ('attribute_id', '=', 1)
                            ],limit=1)
                        else:
                            id_sede = self.env['product.attribute.value'].search([
                                ('name', '=', lead.cod_sede),
                                ('attribute_id', '=', 4)
                            ],limit=1)
                    logger.info("VAMOS A VER LA SEDE")
                    logger.info(id_sede)
                else:
                    logger.info("OTROS mMAS")
                    logger.info(lead.codigo)
                    if lead.codigo == 'ISEP':
                        if lead.sede.lower() == 'isep madrid' or lead.sede.lower() == 'madrid':
                            id_sede = self.env['product.attribute.value'].search([
                                    ('x_descripcion', '=', 'campus Madrid')
                                ],limit=1)
                        if lead.sede.lower() == 'barcelona':
                            id_sede = self.env['product.attribute.value'].search([
                                    ('name', '=', 'CAT')
                                ],limit=1)

            if len(id_sede) != 1:
                logger.info("No hay sede len(id_sede)")
                id_sede = self.env['product.attribute.value'].search([
                                ('x_descripcion', 'ilike', lead.sede),
                            ],limit=1)

            # Duplicidad de Iniciativas #
            logger.info("SEGUIMOS TRABAJANDO")
            numdups = 0
            precontacto = 'Única'
            grupoduplicado = 0
            lista_dup = []
            company_string = ''

            # if lead.codigo != 'ISED':
            dup_lead_obj = self.env['crm.lead'].search([
                ('|'),
                ('phone', '=', lead.phone),
                ('email_from', 'ilike', lead.email),
                ('active', '=', True),
                ('type', '=', 'lead')])

            if dup_lead_obj is None:
                dup_lead_obj = self.env['crm.lead'].search([
                ('|'),
                ('phone', 'ilike', lead.phone[:9]),
                ('email_from', 'ilike', lead.email),
                ('active', '=', True),
                ('type', '=', 'lead')])

            if dup_lead_obj:
                for dup in dup_lead_obj:
                    logger.info("Lead duplicado: %s", dup.name)
                    if dup.company_id.id not in lista_dup:
                        lista_dup.append(dup.company_id.id)
                        company_string = \
                            company_string + ', '
                        company_string = \
                            company_string + str(dup.company_id.name)

                    if dup.x_grupoduplicado != 0:
                        grupoduplicado = dup.x_grupoduplicado
                    else:
                        sql_crm_dup = \
                            "select nextval('crm_lead_x_grupoduplicado_seq') as valor"
                        self._cr.execute(sql_crm_dup)
                        res = self._cr.fetchall()
                        grupoduplicado = res[0]
                        grupoduplicado = grupoduplicado[0]

                    if dup.x_precontactonuevodup == 'Única':
                        sql_crm_dup = \
                            "select nextval('crm_lead_x_grupoduplicado_seq') as valor"
                        self._cr.execute(sql_crm_dup)
                        res = self._cr.fetchall()
                        leadduplicado = res[0]
                        leadduplicado = leadduplicado[0]

                        if len(lista_dup) > 1:
                            precontacto = "Duplicada (%s)%s" % \
                                (leadduplicado, company_string)
                        else:
                            precontacto = "Duplicada(%s)" % (leadduplicado)

                        dup.write({'x_precontactonuevodup': precontacto})

                numdups = len(dup_lead_obj)

                if len(lista_dup) > 1:
                    precontacto = "Duplicada (%s)%s" % \
                        (grupoduplicado, company_string)
                else:
                    precontacto = "Duplicada(%s)" % (grupoduplicado)

            # FIN #

            # Duplicidad de Contactos #
            contactonuevodup = "Nuevo"

            partner_dup = self.env['res.partner'].search([
                ('|'),
                ('|'),
                ('phone', '=', lead.phone),
                ('mobile', '=', lead.phone),
                ('email', 'ilike', lead.email)],
                limit=1)
            if partner_dup is None:
                logger.info("NO LO Encuentra y lo busca")
                logger.info(lead.phone[:9])
                partner_dup = self.env['res.partner'].search([
                    ('|'),
                    ('phone', '=', lead.phone[:9]),
                    ('email', 'ilike', lead.email)],
                    limit=1)

            logger.info("Partner duplicado: %s", partner_dup.name)

            if partner_dup.user_id:
                contactonuevodup = partner_dup.user_id.name

            logger.info("sale del partner duplicado: %s", partner_dup.name)
            # Rellenar posibles códigos que faltan #

            # Código de sede #
            logger.info("Ponemos el código de sede")
            if lead.cod_sede == ' ':
                if id_equipo_ventas.id == 22:
                    sede_llamada = 'MDR'
                else:
                    sede_llamada = id_equipo_ventas.code
            else:
                sede_llamada = lead.cod_sede

            # Código de tipo de curso #
            logger.info("Ponemos el código de Curso")
            curso_init = ''

            if lead.cod_tipo_curso == ' ' and prod_id.tipodecurso != ' ':
                if prod_id.tipodecurso == 'master':
                    curso_init = 'MT'
                elif prod_id.tipodecurso == 'curso':
                    curso_init = 'CU'
                elif prod_id.tipodecurso == 'pgrado':
                    curso_init = 'CU'
            elif prod_id.tipodecurso == '':
                logger.info("Entro en el elif")
                curso_init = ''
            else:
                logger.info("Entro en el else") 
                curso_init = lead.cod_tipo_curso
            # FIN #

            # Código de curso #
            logger.info("Ponemos el código de Curso 2")
            logger.info(lead.cod_curso)
            logger.info(prod_id.default_code)
            try:
                if lead.cod_curso == ' ' or lead.cod_curso == '-':
                    codigo_producto = prod_id.default_code
                    codigo_producto = codigo_producto[:2]
                else:
                    codigo_producto = lead.cod_curso
            except:
                codigo_producto='--'

            # FIN #
            logger.info("Ponemos el código de Curso 3")
            logger.info("codigo_producto: %s", codigo_producto)

            # Parche para caso especifico - error en BBDD #
            logger.info("Curso_INIT")
            logger.info(curso_init)
            try:
                if curso_init == 'CU':
                    tipocurso_id = self.env['x.crmtipodecurso'].search([
                        ('x_codigotipodecurso', '=', 'PR'),
                        ('x_name', '!=', '')
                    ], limit=1)

                else:
                    if len(curso_init)>1:
                        tipocurso_id = self.env['x.crmtipodecurso'].search([
                            ('x_codigotipodecurso', '=', curso_init),
                            ('x_name', '!=', '')
                        ], limit=1)
                    else:
                        logger.info("entramos en el error del tipo de curso")
                        tipocurso_id = self.env['x.crmtipodecurso'].search([
                            ('x_codigotipodecurso', '=', 2),
                            ('x_name', '!=', '')
                        ], limit=1)

            except:
                logger.info("entramos en el error del tipo de curso")
                tipocurso_id = self.env['x.crmtipodecurso'].search([
                    ('x_codigotipodecurso', '=', 7),
                    ('x_name', '!=', '')
                ], limit=1)
            logger.info("tipocurso_id")
            logger.info(tipocurso_id.id)
            logger.info("tipocurso_id")


            # FIN #

            # Generar nombre de iniciativa #
            logger.info("EQUIPO DE VENTAS")
            try:

                if id_equipo_ventas.id == 22:
                    nombre_sede = 'MDR'
                else:
                    nombre_sede = id_equipo_ventas.code

            except:
                logger.info("ERROR EN NOMBRE DE LA SEDE")
                nombre_sede='???'

            try:
                lead_name = prod_id.default_code[:2] + nombre_sede + ' - ' + lead.email
            except:
                logger.info("ERROR EN LA CABECERA DE  LA OPORTUNIDAD")
                lead_name = codigo_producto + nombre_sede + ' - ' + lead.email
                lead_name = '?????- ' + lead.email

            if lead.codigo == 'ISTN':
                lead_name = 'ISTENAC - '+lead_name
                id_equipo_ventas= self.env['crm.team'].browse(26)

            logger.info("EQUIPO DE VENTAS")
            # FIN #

            # Caso de las llamadas internacionales #
            logger.info("FUERA IF INT")
            if lead.curso.lower() == 'protegido: llamada internacional':
                id_equipo_ventas = self.env['crm.team'].search([
                    ('code', '=', 'BCN')
                ])
                id_sede = self.env['product.attribute.value'].search([
                    ('name', '=', 'BCN')
                ])
                logger.info("DENTRO IF INT")

                user_id = self.env['res.users'].browse(45)

            # FIN #

            cliente_obj = self.env['res.partner'].search([
                ('email', '=', lead.email)
            ])

            if len(cliente_obj) > 1:
                cliente_obj = cliente_obj[0]

            if not cliente_obj:
                # logger.info("ENTRO AQUI Y ENSEÑO INFO")
                # logger.info(lead.nombre.capitalize() + ' ' + lead.apellidos.capitalize())
                # logger.info(lead.phone)
                # logger.info(lead.email)
                # logger.info(company_id.id)
                # logger.info(id_equipo_ventas.id)
                # logger.info(user_id.id)
                vals_partner = {
                    'name': lead.nombre.capitalize() + ' ' + lead.apellidos.capitalize(),
                    'phone': lead.phone,
                    'email': lead.email,
                    'company_id': company_id.id,
                    'team_id': id_equipo_ventas.id,
                    'user_id': user_id.id,
                }
                partner_obj = self.env['res.partner']
                cliente_obj = partner_obj.sudo().create(vals_partner)

            # FIN #
            prot_prod = False
            if nombre_curso:
                prot = nombre_curso.split()
            if lead.source == 'Offiline':
                source = 'Offline'
            else:
                source = lead.leadsource

            # Si Portal 1 está vacio, coge valor de Portal 2 #
            if lead.leadsource == '':
                source = lead.source
            # FIN #

            if source == '-' and lead.leadsource != '-':
                source = lead.leadsource

            if nombre_curso:
                prot = nombre_curso.split()
                logger.info('Prot: %s', prot[0])
                if prot[0] == 'Protegido:' or prot[0] == 'Llamada':
                    logger.info("ENTRO AQUI")
                    prot_prod = True

            logger.info("IFNO:")
            logger.info(country_id)
            logger.info(id_sede)
            logger.info(company_id)
            logger.info("VALORES: %s y %s", prod_id, prot_prod)
            logger.info("UNO")
            if country_id or llamada_pais:
                logger.info("DOS")
                logger.info('ID SEDE: %s', id_sede)
                logger.info('COMPANY ID: %s', company_id)
                logger.info('curso_init ID: %s', curso_init)
                logger.info('tipocurso_id : %s', tipocurso_id)
                try:
                    eltipodecurso = tipocurso_id.id
                    logger.info('tipocurso_id.id : %s', tipocurso_id.id)

                except:
                    eltipodecurso = 31
                logger.info('eltipodecurso : %s', eltipodecurso)

                if id_sede and company_id:
                    logger.info("TRES")
                    logger.info(cliente_obj.id)
                    logger.info(lead.nombre + ' ' + lead.apellidos)
                    logger.info(lead.phone)
                    logger.info(lead.descripcion)
                    logger.info(lead.sexo)
                    logger.info(lead.estudios_finalizados)
                    logger.info(lead.cp)
                    logger.info(country_id.id)
                    logger.info(state_id.id)
                    logger.info(lead.ciudad)
                    logger.info(nac)
                    logger.info(lead.email)
                    logger.info(lead.lane)
                    logger.info(company_id.id)
                    logger.info(lead_name)
                    logger.info(date)
                    logger.info(codigo_producto)
                    logger.info(sede_llamada)
                    logger.info(lead.cod_modalidad)
                    logger.info(lead.cod_area)
                    logger.info(lead.estudios_finalizados)
                    logger.info(lead.campanya)
                    logger.info(lead.content)
                    logger.info(lead.medium)
                    logger.info(lead.utma)
                    logger.info(source)
                    
                    logger.info(mod_final.id)
                    logger.info(curso_init)
                    logger.info(user_id.id)
                    logger.info(id_sede.id)
                    logger.info(id_equipo_ventas.id)
                    logger.info(prod_id.id)
                    logger.info("AREA")
                    if area is None:
                        logger.info("EL AREA ESTA VACIA")
                        area.id=self.env['product.category'].browse(1)
                        
                    logger.info(area.id)
                    logger.info(curso.id)
                    logger.info(eltipodecurso)
                    logger.info(grupoduplicado)
                    logger.info(numdups)
                    logger.info(precontacto)
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
                        'country_id': country_id.id or '',
                        'state_id': state_id.id,
                        'city': lead.ciudad,
                        'x_annonacimiento': nac,
                        'email_from': lead.email,
                        'street': lead.lane,
                        'company_id': company_id.id,
                        'name': lead_name,
                        'create_date': date,
                        'x_codcurso': codigo_producto,
                        'x_codsede': sede_llamada,
                        'x_codmodalidad': lead.cod_modalidad,
                        'x_codarea': lead.cod_area,
                        'x_finalizacionestudios': lead.estudios_finalizados,
                        'x_ga_campaign': lead.campanya,
                        'x_content': lead.content,
                        'x_ga_medium': lead.medium,
                        'x_ga_utma': lead.utma,
                        'x_ga_source': source,
                        'x_modalidad_id': mod_final.id,
                        'x_codtipodecurso': curso_init,
                        'user_id': user_id.id,
                        'x_sede_id': id_sede.id,
                        'team_id': id_equipo_ventas.id,
                        'x_producto_id': prod_id.id,
                        'x_area_id': area.id,
                        'x_curso_id': curso.id,
                        'x_tipodecurso_id': eltipodecurso,
                        'x_grupoduplicado': grupoduplicado,
                        'x_numdups': numdups,
                        'x_precontactonuevodup': precontacto
                        }

                    lead_obj = self.env['crm.lead']
                    lead.iniciativa_id = lead_obj.sudo().create(vals_lead).id
                    logger.debug("La inicitiva es ")
                    logger.debug(lead.iniciativa_id)
                    if lead.iniciativa_id:
                        lead.check = True
                        lead.check_error = False
                        lead.error_iniciativa = ''
                    else:
                        logger.info("ERROR!")
        except Exception as e:
            logger.debug("Error")
            logger.debug(e)
            lead.error_iniciativa=e
            lead.check_error = True

    # -- Función para validar las iniciativas -- #
    @api.multi
    def _simple_lead(self, lead):
        cliente_obj = self.env['res.partner'].search([('email', '=', lead.email)])
            # Duplicidad de Contactos #
        contactonuevodup = "Nuevo"

        partner_dup = self.env['res.partner'].search([
            ('|'),
            ('|'),
            ('phone', '=', lead.phone),
            ('mobile', '=', lead.phone),
            ('email', 'ilike', lead.email)],
            limit=1)
        if partner_dup is None:
            logger.info("NO LO Encuentra y lo busca")
            logger.info(lead.phone[:9])
            partner_dup = self.env['res.partner'].search([
                ('|'),
                ('phone', '=', lead.phone[:9]),
                ('email', 'ilike', lead.email)],
                limit=1)

        logger.info("Partner duplicado: %s", partner_dup.name)

        if partner_dup.user_id:
            contactonuevodup = partner_dup.user_id.name

        logger.info("sale del partner duplicado: %s", partner_dup.name)
        # Rellenar posibles códigos que faltan #

        if len(cliente_obj) > 1:
            cliente_obj = cliente_obj[0]
        if lead.pais.encode('utf-8') not in self.rel_country:
            country_id = self.env['res.country'].search([
                ('name', '=', lead.pais),
                ('code', '!=', ''),
                ('create_uid', '!=', None)], limit=1)
            logger.info(country_id)
            if country_id.id is None:
                country_id=self.env['res.company'].browse(1)
        try:
            logger.info("Compañia")
            state_id = self.env['res.country.state'].search([('name', '=', lead.state),('code', '!=', ''),('create_uid', '!=', '')], limit=1)
            #state_id=self.env['res.country.state'].browse(3275)
            logger.info(state_id)
        except:
            logger.info("Error en el estado")
        if lead.codigo.upper()=='ISEP':
            company_id=self.env['res.company'].browse(1)
        else:
            if lead.codigo == 'ISTN':   
                company_id=self.env['res.company'].browse(4)
            else:
                company_id=self.env['res.company'].browse(3)
        logger.info(company_id)
        date = datetime.now()
        if lead.curso=='Becas conecta':
            lead.descripcion ='Becas conecta'

        try:
            logger.info(lead.codigo)
            logger.info(lead.cod_sede)

            lead_name = lead.codigo+lead.cod_sede+ ' - ' + lead.email
        except:
            lead_name =  lead.email

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
            'city': lead.ciudad,
            'x_annonacimiento': 1900,
            'email_from': lead.email,
            'street': lead.lane,
            'company_id': company_id.id,
            'name': lead_name,
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



    # -- Función para validar las iniciativas -- #
    @api.multi
    def _simple_base(self, lead):
        logger.info("********************************************* SIMPLE BASE ")
        logger.info(lead)
        logger.info("********************************************* SIMPLE BASE ")


        cliente_obj = self.env['res.partner'].search([('email', '=', lead.email)])
            # Duplicidad de Contactos #
        contactonuevodup = "Nuevo"

        partner_dup = self.env['res.partner'].search([
            ('|'),
            ('|'),
            ('phone', '=', lead.phone),
            ('mobile', '=', lead.phone),
            ('email', 'ilike', lead.email)],
            limit=1)
        if partner_dup is None:
            logger.info("NO LO Encuentra y lo busca")
            logger.info(lead.phone[:9])
            partner_dup = self.env['res.partner'].search([
                ('|'),
                ('phone', '=', lead.phone[:9]),
                ('email', 'ilike', lead.email)],
                limit=1)

        logger.info("Partner duplicado: %s", partner_dup.name)
        country_id =self.env['res.country'].browse(68)
        logger.info("country_id: %s", country_id)

        if partner_dup.user_id:
            contactonuevodup = partner_dup.user_id.name

        logger.info("sale del partner duplicado: %s", partner_dup.name)
        # Rellenar posibles códigos que faltan #

        if lead.codigo == 'ISEP' and lead.cod_sede=='MAD':
            logger.info("CAMIANDO  MADRID")
            lead.cod_sede='MDR'
        if lead.codigo == 'ISTN':
            lead.cod_sede='IST'
        if lead.cod_sede=='AH!':
            lead.cod_sede='CAT'
            lead.descripcion = "Método at Home"

        if lead.pais != '-':
            if lead.pais != 'Otro':
                llamada_pais = False
                try:
                    if lead.pais.encode('utf-8') not in self.rel_country:
                        logger.info("----------1-----------")
                        country_id = self.env['res.country'].search([('name', '=', lead.pais),('code', '!=', ''),('create_uid', '!=', None)])
                    else:
                        logger.info("----------2-----------")
                        country_id = self.env['res.country'].search([('name', '=', self.rel_country[pais])])

                    if not country_id:
                        logger.info("----------3-----------")
                        country_id = self.env['res.country'].search([('code', 'ilike', lead.pais),('create_uid', '!=', None)])

                    if not country_id:
                        logger.info("----------4-----------")
                        country_id = self.env['res.country'].search([('name', 'ilike', lead.pais),('create_uid', '!=', None),])
                except:
                    country_id = self.env['res.country'].browse(68)
            else:
                llamada_pais = True
                country_id = self.env['res.country'].search([('code', '=', 'vacio')])

        else:
            if lead.phone[:2] == '52':
                country_id = self.env['res.country'].search([('code', '=', 'MX'),('create_uid', '!=', None)])
            elif lead.phone[:2] == '57':
                country_id = self.env['res.country'].search([('code', '=', 'CO'),('create_uid', '!=', None)])

            else:
                llamada_pais = True
                country_id = self.env['res.country'].search([('code', '=', 'vacio')])

        date = datetime.now()

        state_id = self.env['res.country.state'].search([
            ('name', '=', lead.state),
            ('code', '!=', ''),
            ('create_uid', '!=', '')])

        if len(state_id) > 1:
            state_id = state_id[0]
        try:
            logger.info('lead.cod_modalidad: %s', lead.cod_modalidad)
        except:
            lead.cod_modalidad = " "

        id_equipo_ventas = None
        if lead.cod_sede != '-':
            logger.info("NO HAY -")
            if lead.cod_sede != ' ':
                logger.info("TENGO COD SEDE: %s", lead.cod_sede)

                if country_id.code in ['CO', 'MX'] and lead.cod_modalidad != 'PRS':
                    logger.info("Caso 1")
                    try:
                        id_equipo_ventas = self.env['crm.team'].browse(8)
                    except:
                        id_equipo_ventas=None

                elif lead.cod_sede == 'INT':
                    logger.info("ENTRO EN EL INT")
                    id_equipo_ventas = self.env['crm.team'].browse(100000006)

                else:
                    logger.info("Caso 2")
                    if lead.cod_sede == 'ONL':
                        logger.info("Caso 3")
                        if lead.codigo == 'ISED':
                            id_equipo_ventas = self.env['crm.team'].browse(8)
                        logger.info("Caso 4")
                        if lead.codigo == 'ISEP':
                            id_equipo_ventas = self.env['crm.team'].browse(5)
                    else:
                        logger.info("Caso 5")
                        id_equipo_ventas = self.env['crm.team'].browse(7)
            else:
                logger.info("NO TENGO COD SEDE")
                if country_id.code in ['CO', 'MX'] and lead.cod_modalidad != 'PRS':
                    id_equipo_ventas = self.env['crm.team'].browse(100000006)

                else:
                    if lead.sede.lower() == 'sesiones clínicas online':
                        id_equipo_ventas = self.env['crm.team'].browse(5)

                    elif lead.sede.lower() == 'sesiones clínicas valencia':
                        id_equipo_ventas = self.env['crm.team'].browse(19)

                    elif lead.sede.lower() == 'sesiones clínicas barcelona':
                        id_equipo_ventas = self.env['crm.team'].browse(1)

                    elif lead.sede.lower() == 'sesiones clínicas barcelona':
                        id_equipo_ventas = self.env['crm.team'].browse(4)

                    elif lead.sede.lower() == 'isep madrid' or lead.sede.lower() == 'madrid' and lead.codigo == 'ISEP':
                        id_equipo_ventas = self.env['crm.team'].browse(4)

                    elif lead.sede.lower() == 'isep valencia' or lead.sede.lower() == 'valencia' and lead.codigo == 'ISEP':
                        id_equipo_ventas = self.env['crm.team'].browse(19)

                    elif lead.cod_modalidad == 'PRS':
                        if lead.codigo == 'ISED':
                            id_equipo_ventas = self.env['crm.team'].browse(8)

                        if lead.codigo == 'ISEP':
                            id_equipo_ventas = self.env['crm.team'].browse(7)


                    else:
                        id_equipo_ventas = self.env['crm.team'].browse(19)

        if lead.codigo == 'ISTN':
            id_equipo_ventas= self.env['crm.team'].browse(26)

        try:
            company_id = id_equipo_ventas.company_id.id
        except Exception as e:
            logger.info("Produce un error ")
            company_id=1
            if lead.codigo == 'ISED':
                company_id = 3
            else:
                company_id =1
            if lead.codigo == 'ISTN':
                company_id =4
        logger.info("************")
        logger.info("EQUIPO DE VENTAS: %s", id_equipo_ventas)
        logger.info("Compañia VENTAS: %s", company_id)
        logger.info("************")

        try:
            id_equipo = id_equipo_ventas.id
        except:
            id_equipo = 7
        try:
            user_id = id_equipo_ventas.user_id.id
        except:
            user_id=2
        logger.info("************")
        logger.info("user_id : %s", user_id)
        logger.info("id_equipo : %s", id_equipo)
        logger.info("************")
        if len(cliente_obj) > 1:
            cliente_obj = cliente_obj[0]
       
        date = datetime.now()
        if lead.curso=='Becas conecta':
            lead.descripcion ='Becas conecta'

        try:
            logger.info(lead.codigo)
            logger.info(lead.cod_sede)

            lead_name = lead.cod_curso+lead.cod_sede+ ' - ' + lead.email
        except:
            lead_name =  lead.email
        

        logger.info('partner_id  %s',  cliente_obj.id)
        logger.info('contact_name %s',  lead.nombre + ' ' + lead.apellidos)
        logger.info('phone %s',  lead.phone)
        logger.info('description %s',  lead.descripcion)
        logger.info('x_sexo %s', lead.sexo in self.sex and self.sex[lead.sexo] or '')
        logger.info('x_titulacion %s',  lead.estudios_finalizados)
        logger.info('zip %s', lead.cp)
        logger.info('country_id %s',  country_id.id )
        logger.info('state_id %s',  state_id.id )
        logger.info('city %s',  lead.ciudad)
        logger.info('x_annonacimiento %s',  1900)
        logger.info('email_from %s',  lead.email)
        logger.info('street %s', lead.lane)
        logger.info('company_id %s',  company_id)
        logger.info('name  %s',  lead_name)
        logger.info('create_date  %s',  date)
        logger.info('x_codcurso %s',  lead.cod_curso)
        logger.info('x_codsede %s',  lead.cod_sede)
        logger.info('x_codmodalidad %s',  lead.cod_modalidad)
        logger.info('x_codarea %s', lead.cod_area)
        logger.info('x_finalizacionestudios %s',  lead.estudios_finalizados)
        logger.info('x_ga_campaign %s', lead.campanya)
        logger.info('x_content %s', lead.content)
        logger.info('x_ga_medium %s',  lead.medium)
        logger.info('x_ga_utma %s',  lead.utma)
        logger.info('x_ga_source %s',  '')
        logger.info('x_modalidad_id %s',  0)
        logger.info('x_codtipodecurso %s', '')
        logger.info('user_id %s',  user_id )
        logger.info('x_sede_id %s',  0)
        logger.info('team_id %s',  id_equipo)
        logger.info('x_producto_id %s',  0)
        logger.info('x_area_id %s',  0)
        logger.info('x_curso_id %s',  0)
        logger.info('x_tipodecurso_id %s',  '')
        logger.info('x_grupoduplicado %s',  '')
        logger.info('x_numdups %s',  0)
        logger.info('x_precontactonuevodup %s',  '')

        if len(cliente_obj) > 1:
            cliente_obj = cliente_obj[0]
            logger.info(" ya lo ha encontrado")
            logger.info(cliente_obj)


        
        if not cliente_obj:
            logger.info("ENTRO AQUI Y ENSEÑO INFO")
            logger.info(lead.nombre.capitalize() + ' ' + lead.apellidos.capitalize())
            logger.info(lead.phone)
            logger.info(lead.email)
            logger.info(company_id)
            logger.info(id_equipo)
            logger.info(user_id)
            vals_partner = {
                'name': lead.nombre.capitalize() + ' ' + lead.apellidos.capitalize(),
                'phone': lead.phone,
                'email': lead.email,
                'company_id': company_id,
                'team_id': id_equipo,
                'user_id': user_id,
            }
            partner_obj = self.env['res.partner']
            cliente_obj = partner_obj.sudo().create(vals_partner)        
        
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
            'stage_id': 1 ,
            'city': lead.ciudad,
            'x_annonacimiento': 1900,
            'email_from': lead.email,
            'street': lead.lane,
            'company_id': company_id,
            'name': lead_name,
            'create_date': date,
            'x_codcurso': lead.cod_curso,
            'x_codsede':  lead.cod_sede,
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
            'user_id':  user_id,
            'x_sede_id': 0,
            'team_id': id_equipo,
            'x_producto_id': 0,
            'x_area_id': 0,
            'x_curso_id': 0,
            'x_tipodecurso_id': '',
            'x_grupoduplicado': '',
            'x_numdups': 0,
            'x_precontactonuevodup12': contactonuevodup
            }

        lead_obj = self.env['crm.lead']
        lead.iniciativa_id = lead_obj.sudo().create(vals_lead).id

        if lead.iniciativa_id:
            lead.check = True
            lead.check_error = False
            lead.error_iniciativa = ''
        else:
            logger.info("ERROR!")


