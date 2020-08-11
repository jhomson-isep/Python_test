# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'


    @api.multi
    def create(self, lead):

        # Buscar el cliente mediante el email utilizando el self.env en el modelo res.partner
        client = self.env['res.partner'].search([('email', '=', lead.get('email_from'))], limit=1)
        lead.update({'partner_id': client.id})

        # Buscar user id en res.partner
        user = client.user_id.id
        lead.update({'user_id': user})

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
        cod_tipo_curso = lead.get('x_codtipodecurso')
        url = lead.get('x_ga_source')

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
        }

        company_id = None

        #Mediante url enviar a donde debe
        url = lead.get('x_ga_source')
        if url.find("ised") != -1:
            company_id = 4
            logger.info("Entre en ISED")

        elif url.find(".com") != -1:
            company_id = 1111
            logger.info("Entre en LATAM")
        else:
            # lead.update({'company_id': 1})
            company_id = 1
            logger.info("Entre en España")

        #Problemas con el campo mal hecho de modalidad y sede, en los type form se llaman distinto por eso el cambio
        if modalidad == 'Presencial':
            modalidad = 'PRS'
        elif modalidad == 'Online':
            modalidad = 'ELR'

        #Actualizar la modalidad
        lead.update({'x_codmodalidad': modalidad})

        #Dependiendo la sede se le colocara el nombre nuevo
        if cod_sede == 'centro-oviedo':
            cod_sede = 'OVI'
        elif cod_sede == 'centro-bilbao':
            cod_sede = 'BIO'
        elif cod_sede == 'centro-madrid-atocha':
            cod_sede = 'MAD'
        elif cod_sede == 'centro-pamplona':
            cod_sede = 'PAM'
        elif cod_sede == 'centro-zaragoza':
            cod_sede = 'ZAR'



        #REVISAR ESTO
        #Añadir producto a la iniciativa directamente
        logger.info(company_id)
        try:
            referencia_interna = self.env['product_template'].search([('default_code', '=', cod_curso)],limit=1)
            lead.update({'x_curso_id': referencia_interna.id})
            lead.update({'x_producto_id': referencia_interna.id})
        except:
            logger.info("No pudo relacionar la referencia interna con el cod_curso")

        #Crear nombre compuesto de su sede, el codigo y email
        #Elr es online en modalidad
        if modalidad != 'ELR':
            name = cod_curso + cod_sede + " - " + email
        else:
            name = cod_curso + 'ONL' + " - " + email

        lead.update({'name': name})

        #ISEP LATAM
        #---------------------------------
        if company_id == 1111:
            pass

        #ISEP SL
        #---------------------------------
        elif company_id == 1:
            pass

        #ISED
        #---------------------------------
        elif company_id == 4:
            if modalidad == 'ELR':
                #Centro Sup de estudios ISED SL - Online
                company_id = 3
                logger.info("Entre en Online")

            elif cod_sede == 'MAD':
                #Centro de estudios ISED SL - Madrid
                company_id = 4
                logger.info("Entre en Madrid")

            elif cod_sede == 'BIO':
                #Centro de estudios ISED Bilbao - Bilbao
                company_id = 5
                logger.info("Entre en Bilbao")

            elif cod_sede == 'ZAR':
                #Zarised - Zaragoza
                company_id = 6
                logger.info("Entre en Zaragoza")

            else:
                #Iruñised - Pamplona
                company_id = 22
                logger.info("Entre en Iruñised")

        logger.info(lead_copy)
        lead_obj = self.sudo().browse(res.id)
        lead_obj.sudo().write(lead)

        #Update a la base de datos para cambiar el company_id directo
        self.env.cr.execute(
            """ UPDATE crm_lead SET company_id = %s WHERE id = %s""" % (company_id, res.id))

        return res
