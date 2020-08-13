# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'


    @api.model
    def create(self, lead):

        # Buscar el cliente mediante el email utilizando el self.env en el modelo res.partner
        try:
            client = self.env['res.partner'].sudo().search([('email', '=', lead.get('email_from'))], limit=1)
            lead.update({'partner_id': client.id})
        except:
            client = self.env['res.partner'].sudo().create({
                'contact_name': lead.get('contact_name'),
                'partner_name': lead.get('partner_name'),
                'email_from': lead.get('email_from'),
                'mobile': lead.get('mobile'),
                'phone': lead.get('phone')
            })

        company_id = lead.get('company_id')
        logger.info(company_id)

        res = super(CrmLead, self).create(lead)

        #Faltantes en el lead
        lead.update({'x_grupoduplicado': ''})
        lead.update({'x_numdups': 0})
        lead.update({'x_precontactonuevodup': ''})

        #Lógica de las distintas empresas
        nombre = lead.get('name')
        cod_sede = lead.get('x_codsede')
        cod_curso = lead.get('x_codcurso')
        email = lead.get('email_from')
        modalidad = lead.get('x_codmodalidad')
        cod_area = lead.get('x_codarea')
        cod_tipo_curso = lead.get('x_codtipodecurso')
        url = lead.get('website')

        lead_copy = lead
        lead.clear()

        #lead con los nuevos datos hace falta agregar comercial(user_id) y equipo de ventas(crm_team)
        lead = {
            'name': nombre,
            'x_codsede': cod_sede,
            'x_codcurso': cod_curso,
            'email_from': email,
            'x_codtipodecurso':cod_tipo_curso,
            'x_ga_source':url,
            'x_codmodalidad': modalidad,
            'user_id': None,
            'team_id': None,
            'x_modalidad_id': None,
            'x_codarea': cod_area,
            'x_area_id': None,
            'website': None
        }

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
        if modalidad == 'Presencial':
            modalidad = 'PRS'
        elif modalidad == 'Online':
            modalidad = 'ONL'

        #Actualizar la modalidad
        lead.update({'x_codmodalidad': modalidad})

        #Dependiendo la sede se le colocara el nombre nuevo
        if cod_sede == 'centro-oviedo':
            cod_sede = 'OVI'
        elif cod_sede in ('centro-bilbao','bilbao','Bilbao'):
            cod_sede = 'BIO'
        elif cod_sede in ('centro-madrid-atocha', 'madrid', 'Madrid', 'MAD'):
            cod_sede = 'MDR'
        elif cod_sede == 'centro-pamplona':
            cod_sede = 'PAM'
        elif cod_sede == 'centro-zaragoza':
            cod_sede = 'ZAR'

        #REVISAR ESTO
        #Añadir producto a la iniciativa directamente
        logger.info(company_id)
        try:
            referencia_interna = self.env['product.template'].sudo().search([('default_code', 'ilike', cod_curso)], limit=1)
            lead.update({'x_curso_id': referencia_interna.id})

            referencia_interna = self.env['product.product'].sudo().search([('default_code', 'ilike', cod_curso)], limit=1)
            lead.update({'x_producto_id': referencia_interna.id})
        except:
            logger.info("No pudo relacionar la referencia interna con el cod_curso")


        #ISEP LATAM
        #---------------------------------
        if company_id == 1111:
            #Solo se usa online en latam
            #Carolina Araujo
            user_id = 100000006
            team_id = 100000006
            name = cod_curso + cod_tipo_curso + "LATAM" + " - " + email

        #ISEP SL
        #---------------------------------
        elif company_id == 1:
            #Manel Arroyo
            user_id = 76

            if cod_sede in ('barcelona', 'Barcelona', 'BCN'):
                cod_sede = 'CAT'
            elif cod_sede in ('metodo-at-home', 'Metodo-At-Home'):
                cod_sede = 'MAT'
            elif cod_sede in ('valencia', 'Valencia', 'VAL'):
                cod_sede = 'VAL'


            # ONL es online en modalidad
            if modalidad != 'ONL':
                name = cod_curso + "-" + cod_tipo_curso + "-" + cod_sede + "-" + 'PRS' + " - " + email
            else:
                name = cod_curso + "-" + cod_tipo_curso + "-" + cod_sede + "-" + 'ONL' + " - " + email

        #ISED
        #---------------------------------
        elif company_id == 4:

            #ONL es online en modalidad
            if modalidad != 'ONL':
                name = cod_curso + "-" + cod_tipo_curso + "-" + cod_sede + "-" + 'PRS' + " - " + email
            else:
                name = cod_curso + "-" + cod_tipo_curso + "-" + cod_sede + "-" + 'ONL' + " - " + email

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

        #Actualizar el nombre
        lead.update({'name': name})

        #Actualizar id de la modalidad
        try:
            lead.env['product.attribute.value'].sudo().search([('name', 'ilike', modalidad)], limit=1)
            lead.update({'x_modalidad_id': modalidad_id})
        except:
            logger.info("No pudo vincular la modalidad con el codigo de modalidad")

        #Actualizar id del area
        try:
            area_id = lead.env['product.category'].sudo().search([('x_codigocategoria', 'ilike', cod_area)], limit=1)
            lead.update({'x_area_id': area_id.id})
        except:
            logger.info("No pudo vincular el area con el codigo de area")

        logger.info(lead_copy)
        lead_obj = self.sudo().browse(res.id)
        lead_obj.sudo().write(lead)


        #Update a la base de datos para cambiar el company_id directo
        self.env.cr.execute(
            """ UPDATE crm_lead SET company_id = %s WHERE id = %s""" % (company_id, res.id))

        #Update a la base de datos para cambiar el company_id directo
        self.env.cr.execute(
            """ UPDATE crm_lead SET user_id = %s WHERE id = %s""" % (user_id, res.id))

        #Update a la base de datos para cambiar el company_id directo
        self.env.cr.execute(
            """ UPDATE crm_lead SET team_id = %s WHERE id = %s""" % (team_id, res.id))

        return res
