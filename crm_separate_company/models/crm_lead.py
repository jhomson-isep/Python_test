# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.multi
    def create(self, lead):
        logger.info("==========self")
        logger.info(self)
        logger.info("==========self")

        #Buscar el cliente mediante el email utilizando el self.env en el modelo res.partner
        client = self.env['res.partner'].search([('email', '=', lead.get('email_from'))], limit=1)
        lead.update({"partner_id": client.id})

        #Buscar el id del país para poder vincular después
        country_id = self.env['res.country'].search([('id', '=', lead.get('country_id'))])
        lead.update({"country_id": country_id})

        #Buscar el id del status
        state_id = self.env['res.country.state'].search([('id', '=', lead.get('state_id'))])
        lead.update({"state_id": state_id})

        # Test with company_id
        company_id = self.env['res.company'].search([('id', '=', 2)])
        lead.update({"company_id": company_id.id})

        #Buscar user id en res.partner
        user = client.user_id

        #Tomar la fecha actual
        date = datetime.now()

        #Relación de codigo curso con referencia interna
        #cod_curso = self.env['res.product.template'].search([('default_code', '=', lead.get(''))])

        #Hacer update a todos los datos antes de crear el lead
        lead.update({"contact_name": lead.get('contact_name')})
        lead.update({"phone": lead.get('phone')})
        lead.update({"mobile": lead.get('mobile')})

        lead.update({"description": lead.get('description')})
        lead.update({"x_titulacion": lead.get('x_titulacion')})
        lead.update({"zip": lead.get('zip')})

        lead.update({"country_id": lead.get('country_id')})
        lead.update({"city": lead.get('city')})
        lead.update({"x_annonacimiento": lead.get('x_annonacimiento')})

        lead.update({"email_from": lead.get('email_from')})
        lead.update({"street": lead.get('street')})
        #self.company_id = lead.get('company_id')
        #lead.update({"company_id": lead.get('company_id')})

        lead.update({"name": "prueba"})
        lead.update({"create_date": lead.get('create_date')})
        lead.update({"x_codsede": lead.get('x_codsede')})

        lead.update({"x_codmodalidad": lead.get('x_codmodalidad')})
        lead.update({"x_codarea": lead.get('x_codarea')})
        lead.update({"x_finalizacionestudios": lead.get('x_finalizacionestudios')})

        lead.update({"x_ga_campaign": lead.get('x_ga_campaign')})
        lead.update({"x_content": lead.get('x_content')})
        lead.update({"x_ga_medium": lead.get('x_ga_medium')})

        lead.update({"x_ga_utma": lead.get('x_ga_utma')})
        lead.update({"x_ga_source": lead.get('x_ga_source')})
        lead.update({"x_modalidad_id": lead.get('x_modalidad_id')})

        lead.update({"x_codtipodecurso": lead.get('x_codtipodecurso')})
        lead.update({"user_id": user})
        lead.update({"x_sede_id": lead.get('x_sede_id')})

        lead.update({"team_id": lead.get('team_id')})
        lead.update({"x_producto_id": 0})
        lead.update({"x_area_id": 0})

        lead.update({"x_curso_id": 0})
        lead.update({"x_tipodecurso_id": ''})
        lead.update({"x_grupoduplicado": ''})

        lead.update({"x_numdups": 0})
        lead.update({"x_precontactonuevodup": ''})
        lead.update({"type": "lead"})

        logger.info("==========lead")
        logger.info(lead)
        logger.info("==========lead")

        res = super(CrmLead, self).create(lead)
        # logger.info(res)
        # logger.info(lead.get('company_id'))
        # logger.info(lead.get('active'))
        # logger.info(lead.get('x_ga_source'))

        return res

