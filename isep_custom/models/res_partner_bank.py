# -*- coding: utf-8 -*-

from openerp import models, api
from . import iban
import logging
_logger = logging.getLogger(__name__)


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    # Se elimina la constrain de un numero de cuenta unico por compañia.
    #_sql_constraints = [('unique_number', '', 'Account Number must be unique')]

    """
    Proceso que gracias al archivo iban.py transforma los ccc en iban.
    Tiene en cuenta que todos los paises son ES.
    https://www.lawebdelprogramador.com/codigo/Python/3276-Calculo-del-IBAN.html
    """
    @api.model
    def calculo_iban_proceso(self):
        _logger.info("-->> ENTRO calculo_iban_proceso")
        for company in self.env['res.company'].search([]):
            for bank in self.env['res.partner.bank'].search([
                ('company_id', '=', company.id),
                ('acc_type', '=', 'bank')
                    ]):
                _logger.info("BANCOOOOOOO")
                _logger.info(bank)
                _logger.info(bank.acc_number)
                _logger.info("CONVERTIRRRR")
                number = bank.acc_number
                if number[:2] in ('ES', 'es'):
                    number = number[2:]
                iban_number = iban.convertir(number)
                _logger.info(iban_number)
                if ('Error') not in iban_number:
                    bank.acc_number = iban_number
        _logger.info("-->> FIN calculo_iban_proceso")
