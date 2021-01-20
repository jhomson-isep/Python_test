# -*- coding: utf-8 -*-

from ..tools import tools
from ..exceptions.custom_exceptions import InvalidJson
from odoo import http, _
from odoo.http import request


class TypeFormController(http.Controller):

    @http.route(['/typeform/webhook'], type="json", auth="public")
    def send_typeform(self):
        """
            Trae el formulario y lo almacena en base de datos para su visualizacion
        :return: retorna un json con el estado como respuesta
        """
        try:
            response = request.jsonrequest
            tools.convert_response_to_form(response)
            return self._status_response('200', 'OK', _("Form has been successfully registered"))
        except InvalidJson as e:
            return self._status_response('404', 'NOT_FOUND', e)

    def _status_response(self, code, status, description=""):
        return {
            'code': code,
            'status': status,
            'description': description
        }
