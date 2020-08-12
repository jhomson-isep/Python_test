# -*- coding: utf-8 -*-
# © 2018 Qubiq 2010
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import werkzeug
from psycopg2 import OperationalError
from openerp import api, http, registry, SUPERUSER_ID
import logging
import datetime
_logger = logging.getLogger(__name__)


class isepController(http.Controller):

    # Controlador para la entrada de leads desde diferentes portales

    @http.route('/data_entry2', type='http', website=True, auth='none', methods=['GET'], csrf=False)
    def get_lead_data(self, **kw):
        codigo_curso = kw['codigo_curso']

        lista_codigo_curso = codigo_curso.split('_')
        cod_curso = lista_codigo_curso[0]
        cod_sede = lista_codigo_curso[1]
        cod_mod = lista_codigo_curso[2]

        date = datetime.datetime.now()
        lead = {
            'codigo': 'codigo_identidad' in kw and kw['codigo_identidad'] or '',
            'leadsource': 'leadsource' in kw and kw['leadsource'].capitalize() or '',
            'source': 'source' in kw and kw['source'].capitalize() or '',
            'cod_curso': cod_curso,
            'cod_sede': cod_sede,
            'cod_modalidad': cod_mod,
            'nombre': 'firstname' in kw and kw['firstname'].capitalize() or '',
            'apellidos': 'lastname' in kw and kw['lastname'].capitalize() or '',
            'phone': 'phone' in kw and kw['phone'] or '',
            'mobile': 'mobile' in kw and kw['mobile'] or '',
            'email': 'email' in kw and kw['email'] or '',
            'pais': 'country' in kw and kw['country'].capitalize() or '',
            'state': 'state' in kw and kw['state'].capitalize() or '',
            'anno_nac': 'anno_nacimiento' in kw and kw['anno_nacimiento'] or '',
            'ciudad': 'city' in kw and kw['city'].capitalize() or '',
            'estudios_finalizados': 'estudios' in kw and kw['estudios'].capitalize() or '',
            'lane': 'lane' in kw and kw['lane'].capitalize() or '',
            'terms': 'acepta_condiciones' in kw and kw['acepta_condiciones'] or '',
            'cp': 'code' in kw and kw['code'] or '',
            'descripcion': 'description' in kw and kw['description'].capitalize() or '',
            'sexo': 'sexo' in kw and kw['sexo'].capitalize() or '',
            'horario': 'horario_contacto' in kw and kw['horario_contacto'] or '',
            'fecha_lead': date,
            'other': kw,
            'name': cod_curso + cod_sede + ' - ' + ('email' in kw and kw['email'] or ''),
            'code': 'code' in kw and kw['code'].capitalize() or '',
            'campanya': 'campaign' in kw and kw['campaign'].capitalize() or '',
            'id_comercial': 'assigned_user_id' in kw and kw['assigned_user_id'] or '',
            'cod_tipo_curso': 'codigo_tipo_curso' in kw and kw['codigo_tipo_curso'] or '',
            'curso': 'curso' in kw and kw['curso'].capitalize() or '',
            'cod_area': 'codigo_area' in kw and kw['codigo_area'] or '',
            'content': 'content' in kw and kw['content'].capitalize() or '',
            'medium': 'medium' in kw and kw['medium'].capitalize() or '',
            'utma': 'utma' in kw and kw['utma'].capitalize() or '',
            'modalidad': 'modalidad' in kw and kw['modalidad'].capitalize() or '',
            'tipo_curso': 'tipo_curso' in kw and kw['tipo_curso'].capitalize() or '',
            'sede': 'sede' in kw and kw['sede'].capitalize() or '',
            'area': 'area' in kw and kw['area'].capitalize() or '',

        }
        tmp_obj = http.request.env['crm.temp2']
        if tmp_obj.sudo().create(lead):
            return "OK"
