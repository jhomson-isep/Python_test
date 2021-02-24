# -*- coding: utf-8 -*-

# Oh Great Cloud,
#
# Grant me the courage to write the code I can,
# to escalate the tickets I cannot fix,
# and the wisdom to know the difference.
#
# Programming one day at a time,
# enjoying one function at a time;
# accepting bugs as a pathway to code complete;
# taking this terrible codebase as it is;
# not as I would have it;
# trusting that all things will be made right
# if I surrender to writing tests and documentation;
# so that I may be reasonably happy at the end of the day
# and somewhat sane at the end of this release.
#
# Amen

from odoo import models, fields, api, SUPERUSER_ID
import urllib.parse as urlparse
from urllib.parse import parse_qs
from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    zapier = fields.Boolean(string="¿Proviene de Zapier?", default=False)

    @api.model
    def create(self, lead):

        #Añadir campo zapier para saber si proviene de ahí, de no ser así se creará de forma natural
        zapier = lead.get('zapier')
        course = lead.get('x_documentodeidentidad') or None
        if zapier and course != 'Ninguna de las anteriores':
            # Buscar el cliente mediante el email utilizando el self.env en el modelo res.partner, si no existe se crea
            client = self.env['res.partner'].sudo().search([('email', '=ilike', lead.get('email_from'))], limit=1)
            if len(client) > 0:
                try:
                    lead.update({'partner_id': client.id})
                    # Asignar actual <- El actual es cuando una persona ya ha sido atendida anteriormente por algún asesor
                    lead.update({'x_contactonuevoodup12': client.user_id.id or None})
                except Exception as e:
                    logger.info("########## CONTACTO EXISTENTE PERO NO ACTUALIZADO")
                    logger.info(e)
                    logger.info(client)
            else:
                client = self.env['res.partner'].sudo().create({
                    'name': lead.get('contact_name'),
                    'display_name': lead.get('partner_name'),
                    'email': lead.get('email_from'),
                    'mobile': lead.get('mobile') or None,
                    'phone': lead.get('phone') or None,
                    'type': 'contact'
                })
                try:
                    lead.update({'partner_id': client.id})
                except Exception as e:
                    logger.info("########## NO PUDE CREAR Y ASIGNAR EL CONTACTO")
                    logger.info(e)
                    logger.info(client)

            # Lógica de las distintas empresas
            cod_sede = lead.get('x_codsede')
            cod_curso = lead.get('x_codcurso')
            email = lead.get('email_from')
            modalidad = lead.get('x_codmodalidad')
            cod_area = lead.get('x_codarea')
            cod_tipo_curso = lead.get('x_codtipodecurso')
            url = lead.get('website')
            nombre_curso = lead.get('x_universidad')
            telefono = lead.get('phone')
            description = lead.get('description')

            actual = lead.get('x_contactonuevoodup12')
            logger.info(lead.get('x_profesion'))
            logger.info(lead.get('x_finalizacionestudios'))

            #Nombre completo del producto
            try:
                if course.find('[') != -1:
                    cod_curso = course[1:3]
            except Exception as e:
                print(e)

            #---------------Nueva lógica de typeform-----------------------------#
            if cod_sede is None or cod_sede == '':
                cod_sede = lead.get('x_profesion')
            else:
                lead.update({'x_profesion': ''})
            if modalidad is None or modalidad == '':
                modalidad = lead.get('x_finalizacionestudios')
            else:
                lead.update({'x_finalizacionestudios': ''})


            #name
            try:
                if modalidad == 'ONL':
                    lead.update({
                        'name': cod_curso +
                                '-' +
                                modalidad +
                                ' - ' +
                                email
                    })
                elif modalidad == 'ATH':
                    lead.update({
                        'name': cod_curso +
                                '-' +
                                modalidad +
                                ' - ' +
                                email
                    })
                else:
                    lead.update({
                        'name': cod_curso +
                                '-' +
                                modalidad +
                                '-' +
                                cod_sede +
                                ' - ' +
                                email
                    })
            except Exception as e:
                logger.info(e)

            # create
            res = super(CrmLead, self).create(lead)
            fecha = res.create_date
            lead.clear()

            # lead con los nuevos datos hace falta agregar comercial(user_id) y equipo de ventas(crm_team)
            lead = {
                'x_codsede': cod_sede,
                'x_codcurso': cod_curso,
                'email_from': email,
                'x_codtipodecurso': cod_tipo_curso,
                'description': description,
                'x_codmodalidad': modalidad,
                'user_id': None,
                'team_id': None,
                'x_modalidad_id': None,
                'x_codarea': cod_area,
                'x_area_id': None,
                'website': None,
                'x_profesion': None,
                'x_curso_id': None,
                'x_producto_id': None,
                'x_sede_id': None
            }

            try:
                url_parsed = urlparse.urlparse(url)
                campaign = parse_qs(url_parsed.query)['utm_campaign']

                if campaign:
                    lead.update({'x_ga_campaign': campaign[0]})

                medium = parse_qs(url_parsed.query)['utm_medium']
                if medium:
                    lead.update({'x_ga_medium': medium[0]})

                source = parse_qs(url_parsed.query)['utm_source']
                if source:
                    lead.update({'x_ga_source': source[0]})

                term = parse_qs(url_parsed.query)['utm_term']
                if source:
                    lead.update({'x_ga_term': term[0]})

            except Exception as e:
                logger.info(e)

            user_id = None
            team_id = None

            # Mediante url enviar a donde debe
            try:
                if url.find("ised") != -1:
                    company_id = 4
                    logger.info("Entre en ISED")

                elif url.find(".com") != -1:
                    company_id = 1111
                    # Carolina Araujo
                    user_id = 100000006
                    team_id = 100000006
                    logger.info("Entre en LATAM")
                else:
                    company_id = 1
                    # Manel Arroyo
                    user_id = 76
                    # team_id =
                    logger.info("Entre en España")
            except Exception as e:
                logger.info(e)
                company_id = 4
                logger.info("Entre en ISED por error")

            # Problemas con el campo mal hecho de modalidad y sede, en los type form se llaman distinto por eso el cambio
            if modalidad in ('Presencial', 'presencial'):
                modalidad = 'PRS'
            elif modalidad in ('Online', 'online'):
                modalidad = 'ONL'
            # Modalidad At-Home
            elif modalidad in ('at home', 'At Home', 'At home', 'AT HOME - clases y participación en vivo con los mejores expertos, por videoconferencia'):
                modalidad = 'ATH'

            # Actualizar la modalidad
            lead.update({'x_codmodalidad': modalidad})

            # Dependiendo la sede se le colocara el nombre nuevo
            if cod_sede in ('centro-oviedo', 'Oviedo', 'ised-oviedo', 'OviedoOviedo'):
                cod_sede = 'OVI'
            elif cod_sede in ('centro-bilbao', 'bilbao', 'Bilbao', 'ised-bilbao', 'BilbaoBilbao'):
                cod_sede = 'BIO'
            elif cod_sede in ('centro-madrid', 'centro-madrid-atocha', 'madrid', 'Madrid', 'MAD', 'MDR', 'ised-madrid', 'sesiones-clinicas-madrid', 'MadridMadrid'):
                cod_sede = 'MDR'
            elif cod_sede in ('ised-barcelona', 'sesiones-clinicas-barcelona', 'BarcelonaBarcelona'):
                cod_sede = 'CAT'
            elif cod_sede in ('centro-pamplona', 'Pamplona', 'ised-pamplona', 'PamplonaPamplona'):
                cod_sede = 'PAM'
            elif cod_sede in ('centro-zaragoza', 'Zaragoza', 'ZAZ', 'ised-zaragoza', 'ZaragozaZaragoza'):
                cod_sede = 'ZAR'
            elif cod_sede in ('Valencia', 'valencia', 'sesiones-clinicas-valencia', 'ValenciaValencia'):
                cod_sede = 'VAL'
            elif cod_sede in ('Online', 'online', 'sesiones-clinicas-online', 'OnlineOnline', 'Indiferente'):
                cod_sede = 'ONL'

            # REVISAR ESTO
            # Añadir producto a la iniciativa directamente
            logger.info(company_id)
            logger.info(cod_curso)

            # ISEP LATAM
            # ---------------------------------
            if company_id == 1111:
                if modalidad == '001':
                    modalidad = 'ATH'
                    cod_sede = 'CAT'
                elif modalidad == '010':
                    modalidad = 'PRS'
                elif modalidad == '100':
                    modalidad = 'ONL'
                # Solo se usa online en latam
                # Carolina Araujo
                user_id = 100000006
                team_id = 100000006

                lead.update({
                    'name': cod_curso +
                            '-' +
                            modalidad +
                            ' - ' +
                            email
                            })

            # ISEP SL
            # ---------------------------------
            elif company_id == 1:
                #Codigo de modalidad con la logica de typeform
                if modalidad == '001':
                    modalidad = 'ATH'
                    cod_sede = 'CAT'
                elif modalidad == '010':
                    modalidad = 'PRS'
                elif modalidad == '100':
                    modalidad = 'ONL'

                no_lead = False
                if description.find('Agente internacional-') != -1:
                    #Agentes internacionales Yura Vanegas
                    user_id = 45
                    no_lead = True
                elif description.find('Diplomado-') != -1:
                    #Diplomado Alicia Pinto
                    user_id = 255
                    no_lead = True
                elif description.find('Sesión'):
                    no_lead = True
                else:
                    # Manel Arroyo
                    user_id = 76

                if cod_sede in ('centro-barcelona', 'barcelona', 'Barcelona', 'BCN', '001'):
                    cod_sede = 'CAT'
                    team_id = 1
                    lead.update({'x_sede_id': 2})

                elif cod_sede in ('metodo-at-home', 'Metodo-At-Home') or modalidad == 'ATH':
                    cod_sede = 'ATH'
                    team_id = 1
                    lead.update({'x_sede_id': 2})

                elif cod_sede in ('valencia', 'Valencia', 'VAL', '100'):
                    cod_sede = 'VAL'
                    team_id = 200000001
                    lead.update({'x_sede_id': 5})

                elif cod_sede == 'ONL' or modalidad == 'ONL':
                    team_id = 5
                    lead.update({'x_sede_id': 26})
                    # Mandar a Latam cuando sea un telefono de México y Colombia
                    if telefono[:3] in ('+52', '+57') or telefono[:2] in ('52', '57'):
                        company_id = 1111
                        # Carolina Araujo
                        user_id = 100000006
                        team_id = 100000006

                elif cod_sede in ('MDR', '100'):
                    team_id = 4
                    lead.update({'x_sede_id': 3})

                if modalidad == 'ONL' and no_lead:
                    lead.update({
                        'name': cod_curso +
                                '-' +
                                modalidad +
                                ' - ' +
                                email
                                })
                elif modalidad == 'ATH' and no_lead:
                    lead.update({
                        'name': cod_curso +
                                '-' +
                                modalidad +
                                ' - ' +
                                email
                                })
                elif modalidad == 'PRS' and no_lead:
                    lead.update({
                        'name': cod_curso +
                                '-' +
                                modalidad +
                                '-' +
                                cod_sede +
                                ' - ' +
                                email
                                })

                lead.update(({'x_codmodalidad': modalidad}))
                lead.update(({'x_codsede': cod_sede}))

            # ISED
            # ---------------------------------
            elif company_id == 4:

                #Codigo de sede con la logica de typeform
                if cod_sede == '00001':
                    cod_sede = 'ONL'
                    lead.update({'x_sede_id': 13})
                elif cod_sede == '00010':
                    cod_sede = 'PAM'
                    lead.update({'x_sede_id': 9})
                elif cod_sede == '00100':
                    cod_sede = 'BIO'
                    lead.update({'x_sede_id': 10})
                elif cod_sede == '01000':
                    cod_sede = 'ZAR'
                    lead.update({'x_sede_id': 11})
                elif cod_sede == '10000':
                    cod_sede = 'MDR'
                    lead.update({'x_sede_id': 8})

                #Codigo de modalidad con la logica de typeform
                if modalidad == '001':
                    modalidad = 'ATH'
                elif modalidad == '010':
                    modalidad = 'PRS'
                elif modalidad == '100':
                    modalidad = 'ONL'

                if modalidad:
                    if modalidad == 'ONL':
                        lead.update({
                            'name': cod_curso +
                                    '-' +
                                    modalidad +
                                    ' - ' +
                                    email
                                    })
                    elif modalidad == 'ATH':
                        lead.update({
                            'name': cod_curso +
                                    '-' +
                                    modalidad +
                                    ' - ' +
                                    email
                                    })
                    else:
                        lead.update({
                            'name': cod_curso +
                                    '-' +
                                    modalidad +
                                    '-' +
                                    cod_sede +
                                    ' - ' +
                                    email
                                    })

                lead.update(({'x_codmodalidad': modalidad}))
                lead.update(({'x_codsede': cod_sede}))

                # ONL es online en modalidad

                if modalidad == 'ONL' or cod_sede == 'ONL' or cod_sede == 'CAT' or modalidad == 'ATH':
                    # Centro Sup de estudios ISED SL - Online
                    # company_id = 3
                    # Yura Vanegas
                    user_id = 45
                    team_id = 8
                    logger.info("Entre en Online")

                elif cod_sede == 'MDR':
                    # Centro de estudios ISED SL - Madrid
                    # company_id = 4
                    # Karoll Rodríguez
                    user_id = 102
                    team_id = 10
                    logger.info("Entre en Madrid")

                elif cod_sede == 'BIO':
                    # Centro de estudios ISED Bilbao - Bilbao
                    # company_id = 5
                    # ISED BILBAO
                    user_id = 189
                    team_id = 12
                    logger.info("Entre en Bilbao")

                elif cod_sede == 'ZAR':
                    # Zarised - Zaragoza
                    # company_id = 6
                    # Silvia Revilla
                    user_id = 105
                    team_id = 11
                    logger.info("Entre en Zaragoza")

                elif cod_sede == 'OVI':
                    user_id = 102
                    team_id = 10
                    logger.info("Oviedo")

                elif cod_sede == 'PAM':
                    # Iruñised - Pamplona
                    company_id = 22
                    # Laura Ollo
                    user_id = 115
                    # team_id = 10
                    logger.info("Entre en Iruñised")
                else:
                    company_id = 4

            #Actual problema
            if actual == None:
                try:
                    lead.update({'x_contactonuevoodup12': user_id})
                except Exception as e:
                    logger.info(e)


            #Producto
            try:
                if modalidad == 'ONL' and company_id == 4:
                    cod_curso = cod_curso + modalidad

                #error con España
                if company_id == 1:
                    referencia_interna_template = self.env['product.template'].sudo().search(
                        [('sale_ok', '=', True),
                         ('default_code', '=', cod_curso),
                         ('company_id', 'in', (1, 1111))], limit=1)
                    logger.info(referencia_interna_template)
                    lead.update({'x_curso_id': referencia_interna_template.id})
                    logger.info(lead.get('x_curso_id'))
                    logger.info("Se actualizo")
                else:
                    referencia_interna_template = self.env['product.template'].sudo().search(
                        [('sale_ok', '=', True),
                         ('default_code', '=', cod_curso),
                         ('company_id', '=', company_id)], limit=1)
                    logger.info(referencia_interna_template)
                    lead.update({'x_curso_id': referencia_interna_template.id})
                    logger.info(lead.get('x_curso_id'))
                    logger.info("Se actualizo")

                referencia_interna_product = self.env['product.product'].sudo().search(
                    [('product_tmpl_id', '=', referencia_interna_template.id)], limit=1)
                logger.info(referencia_interna_product)
                lead.update({'x_producto_id': referencia_interna_product.id})
                logger.info(lead.get('x_producto_id'))

                if len(referencia_interna_template) < 1:
                    referencia_interna_template = self.env['product.template'].sudo().search(
                        [('sale_ok', '=', True),
                         ('name', '=', cod_curso),
                         ('company_id', '=', company_id)], limit=1)
                    logger.info(referencia_interna_template)
                    lead.update({'x_curso_id': referencia_interna_template.id})
                    logger.info(lead.get('x_curso_id'))
                    logger.info("Se actualizo")

                    referencia_interna_product = self.env['product.product'].sudo().search(
                        [('product_tmpl_id', '=', referencia_interna_template.id)], limit=1)
                    logger.info(referencia_interna_product)
                    lead.update({'x_producto_id': referencia_interna_product.id})
                    logger.info(lead.get('x_producto_id'))

            except Exception as e:
                logger.info(e)
                logger.info("No pudo relacionar la referencia interna con el cod_curso")


            # Actualizar id de la modalidad
            try:
                modalidad_id = self.env['product.attribute.value'].sudo().search(
                    [('name', 'ilike', modalidad), ('attribute_id', 'in', [2, 3])], limit=1)
                lead.update({'x_modalidad_id': modalidad_id.id})
            except Exception as e:
                logger.info("===== Fallo en modalidad_id ======")
                logger.info(e)
                logger.info("No pudo vincular la modalidad con el codigo de modalidad")

            # Actualizar id del area
            try:
                area_id = self.env['product.category'].sudo().search([('x_codigocategoria', 'ilike', cod_area)], limit=1)
                lead.update({'x_area_id': area_id.id})
            except Exception as e:
                logger.info("===== Fallo en area_id ======")
                logger.info(cod_area)
                logger.info(e)
                logger.info("No pudo vincular el area con el codigo de area")

            # =======INICIO REVISAR========
            logger.info(lead)
            lead_obj = self.sudo().browse(res.id)
            lead_obj.sudo().write(lead)
            # Update a la base de datos para cambiar el company_id directo
            self.env.cr.execute(
                """ UPDATE crm_lead SET company_id = %s, user_id = %s, team_id = %s WHERE id = %s""" % (
                    company_id, user_id, team_id or 'NULL',  res.id))
            if len(client) > 0:
                self.env.cr.execute(
                    """ UPDATE res_partner SET company_id = %s WHERE id 
                    = %s""" % (company_id, client.id))

            return res
        else:
            # create
            res = super(CrmLead, self).create(lead)
            return res
