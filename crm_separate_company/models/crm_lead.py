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

        self.sudo(2)
        #logger.info(lead)

        # Buscar el id del país para poder vincular después
        #country_id = self.env['res.country'].search([('code', '=', lead.get('country_id'))])
        #lead.update({"country_id": country_id.id})

        # Buscar el id del estado del país
        #state_id = self.env['res.country.state'].search([('code', '=', lead.get('state_id'))])
        #lead.update({"state_id": state_id.id})

        # Buscar user id en res.partner
        #user = client.user_id.id

        # Tomar la fecha actual
        date = datetime.now()

        # Relación de codigo curso con referencia interna
        # cod_curso = self.env['res.product.template'].search([('default_code', '=', lead.get(''))])

        # Hacer update a todos los datos antes de crear el lead
        lead.update({'contact_name': lead.get('contact_name')})
        lead.update({'phone': lead.get('phone')})
        lead.update({'mobile': lead.get('mobile')})

        #lead.update({"description": lead.get('description')})
        lead.update({'x_titulacion': lead.get('x_titulacion')})
        lead.update({'zip': lead.get('zip')})

        lead.update({'country_id': lead.get('country_id')})
        lead.update({'city': lead.get('city')})
        lead.update({'x_annonacimiento': lead.get('x_annonacimiento')})

        lead.update({'email_from': lead.get('email_from')})
        lead.update({'street': lead.get('street')})
        # lead.update({"company_id": lead.get('company_id')})

        #lead.update({"name": lead.get('name')})

        lead.update({'x_codsede': lead.get('x_codsede')})

        #lead.update({"x_codmodalidad": lead.get('x_codmodalidad')})
        lead.update({'x_codarea': lead.get('x_codarea')})
        lead.update({'x_finalizacionestudios': lead.get('x_finalizacionestudios')})

        lead.update({'x_ga_campaign': lead.get('x_ga_campaign')})
        lead.update({'x_content': lead.get('x_content')})
        lead.update({'x_ga_medium': lead.get('x_ga_medium')})

        lead.update({'x_ga_utma': lead.get('x_ga_utma')})
        lead.update({'x_ga_source': lead.get('x_ga_source')})
        lead.update({'x_modalidad_id': lead.get('x_modalidad_id')})

        lead.update({'x_codtipodecurso': lead.get('x_codtipodecurso')})
        #lead.update({'user_id': user})
        lead.update({'x_sede_id': lead.get('x_sede_id')})

        lead.update({'team_id': lead.get('team_id')})
        #lead.update({"x_producto_id": 0})
        #lead.update({"x_area_id": 0})

        #lead.update({"x_curso_id": 0})
        #lead.update({"x_tipodecurso_id": ''})
        lead.update({'x_grupoduplicado': ''})

        lead.update({'x_numdups': 0})
        lead.update({'x_precontactonuevodup': ''})
        #lead.update({"type": "lead"})
        #lead.update({"company_id": lead.get('company_id')})

        #Lógica de las distintas empresas
        nombre = lead.get('name')
        cod_sede = lead.get('x_codsede')
        cod_curso = lead.get('x_codcurso')
        email = lead.get('email_from')
        modalidad = lead.get('x_codmodalidad')
        cod_tipo_curso = lead.get('x_codtipodecurso')
        url = lead.get('x_ga_source')

        lead.clear()

        lead = {
            'name': nombre,
            'x_codsede': cod_sede,
            'x_codcurso': cod_curso,
            'email_from': email,
            'x_codtipodecurso':cod_tipo_curso,
            #'company_id': 0,
            'x_ga_source':url,
            'x_codmodalidad': modalidad,
            'user_id': False
        }

        #Mediante url enviar a donde debe
        url = lead.get('x_ga_source')
        if url.find("ised") != -1:
            lead.update({'company_id': 4})
            #ISED MADRID
            logger.info("Entre en ISED")

        elif url.find(".com") != -1:
            lead.update({'company_id': 1111})
            logger.info("Entre en LATAM")
        else:
            lead.update({'company_id': 1})
            logger.info("Entre en España")

        company_id = lead.get('company_id')
        #Problemas con el campo mal hecho de modalidad y sede, en los type form se llaman distinto por eso el cambio
        if modalidad == 'Presencial':
            modalidad = 'PRS'
        elif modalidad == 'Online':
            modalidad = 'ELR'
            lead.update({'company_id': 3})

        #Actualizar la modalidad
        lead.update({'x_codmodalidad': modalidad})


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
        if modalidad != 'ELR':
            name = cod_sede + cod_curso + " - " + email
        else:
            name = 'ONL' + cod_curso + " - " + email

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
                #lead.update({'company_id': 3})
                logger.info("Entre en Online")

            elif cod_sede == 'MAD':
                #Centro de estudios ISED SL - Madrid
                #lead.update({'company_id': 4})
                logger.info("Entre en Madrid")

            elif cod_sede == 'BIO':
                #Centro de estudios ISED Bilbao - Bilbao
                #lead.update({'company_id': 5})
                logger.info("Entre en Bilbao")

            elif cod_sede == 'ZAR':
                #Zarised - Zaragoza
                #lead.update({'company_id': 6})
                logger.info("Entre en Zaragoza")

            else:
                #Iruñised - Pamplona
                #lead.update({'company_id': 22})
                logger.info("Entre en Iruñised")

        #logger.info('\n Company ID \n')
        #logger.info(lead.get('company_id'))

        logger.info(lead)

        res.sudo().write(lead)

        return res
