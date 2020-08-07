# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError
from lxml import etree
import logging
import base64
import re
from unicodedata import normalize


_logger = logging.getLogger(__name__)
class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'
	
    @api.multi
    def generate_payment_file(self):
        """Creates the txt file. That's the important code !"""
        self.ensure_one()
        clientes = []
        _logger.debug("Entro a debugar APO")
        if self.company_id.id != 1:
            return super(AccountPaymentOrder, self)
        file_lines = []
        for line in self.bank_line_ids:            
            if not line.partner_id.payment_token_ids:
                clientes.append(line.partner_id.name)              
            
            tab = "\t"
            breakline = "\n"
            nombrecliente = line.partner_id.name or ""
            numtarjetacliente = line.partner_id.payment_token_ids and line.partner_id.payment_token_ids[0].acquirer_ref or ""
            cantidadapagar = str(line.amount_currency) + "0" or ""
            emailcliente = line.partner_id.email or ""
            communication = line.communication or ""
            linetab = nombrecliente + tab + numtarjetacliente + tab + cantidadapagar + tab + emailcliente + tab + communication + breakline            
            linetab = self.eliminaracentos(linetab).lower().replace(u"ñ","n")
            file_lines.append(linetab)            
        if len(clientes) > 0:
            strtopr = str(clientes).strip('[]')
            raise UserError("No existe tarjeta de crédito registrada para los clientes {}".format(strtopr))

        return self.file_creation(file_lines)

    def eliminaracentos(self,cad):
        newstr = re.sub(
                r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
                normalize( "NFD", cad), 0, re.I
                )
        newstr = normalize('NFC',newstr)
        return newstr        
    
    @api.multi
    def file_creation(self, file_lines):
        filename = '%s%s.txt' % ("_", self.name)
        
        finalstr = ""
        
        #file = open(filename, "w")
        
        for line in file_lines:
            finalstr += line
        #file.close        

        #filename = '%s%s.txt' % ("_", self.name)
        return (str.encode(finalstr), filename)
