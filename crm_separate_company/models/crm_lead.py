# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID
import urllib.parse as urlparse
from urllib.parse import parse_qs
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'


    @api.model
    def create(self, lead):

        # Buscar el cliente mediante el email utilizando el self.env en el modelo res.partner, si no existe se crea
        client = self.env['res.partner'].sudo().search([('email', '=', lead.get('email_from'))], limit=1)
        if len(client) > 0:
            lead.update({'partner_id': client.id})
        else:
            client = self.env['res.partner'].sudo().create({
                'name': lead.get('contact_name'),
                'display_name': lead.get('partner_name'),
                'email': lead.get('email_from'),
                'mobile': lead.get('mobile'),
                'phone': lead.get('phone')
            })
            lead.update({'partner_id': client.id})


        #Lógica de las distintas empresas
        cod_sede = lead.get('x_codsede')
        cod_curso = lead.get('x_codcurso')
        email = lead.get('email_from')
        modalidad = lead.get('x_codmodalidad')
        cod_area = lead.get('x_codarea')
        cod_tipo_curso = lead.get('x_codtipodecurso')
        url = lead.get('website')
        nombre_curso = lead.get('x_universidad')

        #create
        res = super(CrmLead, self).create(lead)


        lead_copy = lead
        lead.clear()

        #lead con los nuevos datos hace falta agregar comercial(user_id) y equipo de ventas(crm_team)
        lead = {
            'x_codsede': cod_sede,
            'x_codcurso': cod_curso,
            'email_from': email,
            'x_codtipodecurso':cod_tipo_curso,
            'description': url,
            'x_codmodalidad': modalidad,
            'user_id': None,
            'team_id': None,
            'x_modalidad_id': None,
            'x_codarea': cod_area,
            'x_area_id': None,
            'website': None,
            'x_universidad': None
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

        #Mediante url enviar a donde debe
        if url.find("ised") != -1:
            company_id = 4 
            logger.info("Entre en ISED")

        elif url.find(".com") != -1:
            company_id = 1111
            #Carolina Araujo
            user_id = 100000006
            team_id = 100000006
            logger.info("Entre en LATAM")
        else:
            company_id = 1
            #Manel Arroyo
            user_id = 76
            #team_id =
            logger.info("Entre en España")

        #Problemas con el campo mal hecho de modalidad y sede, en los type form se llaman distinto por eso el cambio
        if modalidad in ('Presencial','presencial'):
            modalidad = 'PRS'
        elif modalidad in ('Online', 'online'):
            modalidad = 'ONL'
        #Modalidad At-Home
        elif modalidad in ('at home', 'At Home', 'At home'):
            modalidad = 'ELR'

        #Actualizar la modalidad
        lead.update({'x_codmodalidad': modalidad})

        #Dependiendo la sede se le colocara el nombre nuevo
        if cod_sede == 'centro-oviedo':
            cod_sede = 'OVI'
        elif cod_sede in ('centro-bilbao','bilbao','Bilbao'):
            cod_sede = 'BIO'
        elif cod_sede in ('centro-madrid-atocha', 'madrid', 'Madrid', 'MAD', 'MDR'):
            cod_sede = 'MDR'
        elif cod_sede == 'centro-pamplona':
            cod_sede = 'PAM'
        elif cod_sede == 'centro-zaragoza':
            cod_sede = 'ZAR'

        #REVISAR ESTO
        #Añadir producto a la iniciativa directamente
        logger.info(company_id)
        try:
            referencia_interna_template = self.env['product.template'].sudo().search([('sale_ok', '=', True), ('name', 'ilike', nombre_curso)], limit=1)
            lead.update({'x_curso_id': referencia_interna_template.id})

            referencia_interna_product = self.env['product.product'].sudo().search([('product_tmpl_id', '=', referencia_interna_template.id)], limit=1)
            lead.update({'x_producto_id': referencia_interna_product.id})
        except:
            logger.info("No pudo relacionar la referencia interna con el cod_curso")


        #ISEP LATAM
        #---------------------------------
        if company_id == 1111:
            #Solo se usa online en latam
            #Carolina Araujo
            user_id = 100000006
            team_id = 100000006

        #ISEP SL
        #---------------------------------
        elif company_id == 1:
            #Manel Arroyo
            user_id = 76

            if cod_sede in ('barcelona', 'Barcelona', 'BCN'):
                cod_sede = 'CAT'
                team_id = 1
            elif cod_sede in ('metodo-at-home', 'Metodo-At-Home'):
                cod_sede = 'MAH'
                team_id = 1
            elif cod_sede in ('valencia', 'Valencia', 'VAL'):
                cod_sede = 'VAL'
                team_id = 200000001
            elif cod_sede == 'ONL':
                team_id = 5
            elif cod_sede == 'MDR':
                team_id = 4

            # ONL es online en modalidad
            if modalidad == 'ONL':
                team_id = 5

        #ISED
        #---------------------------------
        elif company_id == 4:

            #ONL es online en modalidad

            if modalidad == 'ONL':
                #Centro Sup de estudios ISED SL - Online
                #company_id = 3
                #Manel Arroyo
                user_id = 76
                team_id = 8
                logger.info("Entre en Online")

            elif cod_sede == 'MDR':
                #Centro de estudios ISED SL - Madrid
                #company_id = 4
                #Karoll Rodríguez
                user_id = 102
                team_id = 10
                logger.info("Entre en Madrid")

            elif cod_sede == 'BIO':
                #Centro de estudios ISED Bilbao - Bilbao
                #company_id = 5
                #ISED BILBAO
                user_id = 189
                team_id = 12
                logger.info("Entre en Bilbao")

            elif cod_sede == 'ZAR':
                #Zarised - Zaragoza
                #company_id = 6
                #Silvia Revilla
                user_id = 105
                team_id = 11
                logger.info("Entre en Zaragoza")

            elif cod_sede == 'OVI':
                user_id = 102
                team_id = 10
                logger.info("Oviedo")

            else:
                #Iruñised - Pamplona
                #company_id = 22
                #Laura Ollo
                user_id = 115
                #team_id = 10
                logger.info("Entre en Iruñised")

        #Actualizar id de la modalidad
        try:
            modalidad_id = self.env['product.attribute.value'].sudo().search(
                [('name', 'ilike', modalidad), ('attribute_id', 'in', [2, 3])], limit=1)
            lead.update({'x_modalidad_id': modalidad_id.id})
        except Exception as e:
            logger.info("===== Fallo en modalidad_id ======")
            logger.info(e)
            logger.info("No pudo vincular la modalidad con el codigo de modalidad")

        #Actualizar id del area
        try:
            area_id = self.env['product.category'].sudo().search([('x_codigocategoria', 'ilike', cod_area)], limit=1)
            lead.update({'x_area_id': area_id.id})
        except Exception as e:
            logger.info("===== Fallo en area_id ======")
            logger.info(cod_area)
            logger.info(e)
            logger.info("No pudo vincular el area con el codigo de area")

        #=======INICIO REVISAR========
        #Buscar si esta duplicada por email y curso
        #lead_dup_ids = self.env['crm.lead'].sudo().search([('email_from', '=', email), ('x_curso_id', '=', referencia_interna_template.id), ('x_modalidad_id', '=', modalidad_id.id)]).ids
        lead_dup_ids = self.env['crm.lead'].sudo().search(
            [('email_from', '=', email), ('x_codcurso', '=', cod_curso),
             ('x_codarea', '=', cod_area), (
                 'name', 'ilike', cod_curso), ('name', 'ilike', modalidad)]).ids


        if len(lead_dup_ids) > 1:
            logger.info("=================DUPLICADO================")
            logger.info("Esta duplicado")
            lead_dup = self.env['crm.lead'].sudo().search(['id', '=', res.id])
            #Elimina el registro que se creo porque ya estaba duplicado
            lead.update({'active': False})
            #Buscar motivo de perdida
            lost_reason = self.env['crm.lost.reason'].sudo().search(['name', 'ilike', 'DUPLICADO'], limit=1)
            lead.update({'lost_reason': lost_reason.id})

        # =======FINAL REVISAR========

        logger.info(lead_copy)
        lead_obj = self.sudo().browse(res.id)
        lead_obj.sudo().write(lead)
        # Update a la base de datos para cambiar el company_id directo
        self.env.cr.execute(
            """ UPDATE crm_lead SET company_id = %s, user_id = %s, team_id = %s  WHERE id = %s""" % (company_id, user_id, team_id, res.id))


        return res