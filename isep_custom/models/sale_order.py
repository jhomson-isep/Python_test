# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError
#from gmri import *
#from . import gmri
#import gmri
import logging
import unicodedata
from datetime import datetime, date, time, timedelta
import urllib.request
import requests 
import traceback

_logger = logging.getLogger(__name__)

def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '%.12f' % f
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])


def UTF8d(valor):
    s = ''.join((c for c in unicodedata.normalize('NFD',valor) if unicodedata.category(c) != 'Mn'))
    return s

def UTF8(cadena):
    s = ''.join((c for c in unicodedata.normalize('NFD',str(cadena)) if unicodedata.category(c) != 'Mn'))
    return s  

def Dato(valor):
    if valor is None:
        return ''
    else:
        return valor

class sale_order(models.Model):
    _inherit = 'sale.order' 

    x_Titular_Factura = fields.Char(string="Titular Factura")
    x_Tarjeta = fields.Char(string="Tarjeta de Crédito", readonly=True)
    x_Recibo_Forma_Pago = fields.Many2one('payment.acquirer', string="Forma de Pago de los Recibos", readonly=True)
    x_Paga_y_Senyal_Vencimiento = fields.Date(string="Fecha de Vencimiento de la Paga y Señal")
    x_Paga_y_Senyal_Pagada = fields.Boolean(string="Paga y señal pagada")
    x_Paga_y_Senyal_Fecha_Pago = fields.Date(string="Fecha de Pago de la Paga y Señal")
    x_Paga_y_Senyal = fields.Monetary(string="Paga y señal")
    x_move_id = fields.Many2one('account.move', string="Asiento contable")
    x_Mes = fields.Integer(string="Mes", readonly=True)
    x_Matricula_Vencimiento = fields.Date(string="Fecha de Vencimiento de la Matrícula")
    x_Matricula_Pagada = fields.Boolean(string="Matrícula pagada")
    x_Matricula_Forma_Pago = fields.Many2one('payment.acquirer', string="Forma de Pago de la Matrícula")
    x_Matricula_Fecha_Pago = fields.Date(string="Fecha de Pago de Matrícula")
    x_GrupoReferencia = fields.Char(string="Grupo de Referencia")
    x_Fecha_Primer_Recibo = fields.Date(string="Fecha Primer Recibo")  # Tiene que ser requerido
    x_Desea_Factura = fields.Boolean(string="Desea Factura")
    x_CVC = fields.Char(string="Código CVC", readonly=True)
    x_CCC = fields.Char(string="Código CCC", readonly=True)
    x_Anyo_Academico = fields.Integer(string="Año Académico")
    x_Anyo = fields.Integer(string="Año", readonly=True)
    x_pago_id = fields.Many2one('isep.pagos', string="Pago", copy=False)
    x_enviado_crm = fields.Boolean(string="Enviado al CRM", default=False, copy=False)
    curso = fields.Boolean(string="Curso", default=True)
    #diario_id = fields.Many2one('account.journal', string="Diario", compute="_get_diario", readonly=True)
    precio_matricula = fields.Float(compute='_get_precio_matricula', string='Precio matrícula', digits=(12, 2))
    precio_entrega = fields.Float(compute='_get_precio_gastos_entrega', string='Precio entrega', digits=(12, 2))
    precio_primer_pago = fields.Float(compute='_get_primer_pago_mensual', string='Precio primer pago', digits=(12, 2))
    precio_ultimo_pago = fields.Float(compute='_get_ultimo_pago_mensual', string='Precio último pago', digits=(12, 2))
    precio_total_curso = fields.Float(compute='_get_total_cursos', string='Precio total curso', digits=(12, 2))
    len_cuotas = fields.Integer(compute="_get_cuotas", string="Quotas")
    fecha_primer_pago = fields.Date(compute="_get_fecha_primer_pago", string="Fecha primer pago")
    cuenta_bancaria = fields.Many2one('res.partner.bank', string="Cuenta bancaria")
    tarjeta_credito = fields.Many2one('account.payment.method', string="Tarjeta de crédito")
    payment_mode_id_name = fields.Char(string="nombre modo de pago", related="payment_mode_id.name")
    mandate_id = fields.Many2one('account.banking.mandate', string="Mandato")
    has_credit_card = fields.Boolean(string="Tarjeta de Crédito (Si/No)", readonly=True, compute="_get_first_card")
    # has_credit_card = fields.Boolean(string="Tarjeta de Crédito (Si/No)")

    @api.multi
    def _get_fecha_primer_pago(self):
        for sel in self:
            if sel.x_pago_id:
                for line in sel.x_pago_id.lines_ids:
                    if 'Pago 1 de' in line.name:
                        sel.fecha_primer_pago = line.fecha_informe

    @api.multi
    def _get_cuotas(self):
        for sel in self:
            size = 0
            if sel.payment_term_id:
                size = len(sel.payment_term_id.line_ids)
            sel.len_cuotas = size

    @api.multi
    def _get_precio_matricula(self):
        for sel in self:
            if sel.x_pago_id:
                price = 0.00
                for line in sel.x_pago_id.lines_ids:
                    if 'Matr' in line.name:
                        price = line.importe
                        break
                sel.precio_matricula = price

    @api.multi
    def _get_precio_gastos_entrega(self):
        for sel in self:
            if sel.x_pago_id:
                price = 0.00
                for line in sel.x_pago_id.lines_ids:
                    if 'Gastos de envio' in line.name:
                        price = line.importe
                        break
                sel.precio_entrega = price

    @api.multi
    def _get_primer_pago_mensual(self):
        for sel in self:
            if sel.x_pago_id:
                price = 0.00
                for line in sel.x_pago_id.lines_ids:
                    if 'Pago 1 de' in line.name:
                        price = line.importe
                        break
                sel.precio_primer_pago = price

    @api.multi
    def _get_ultimo_pago_mensual(self):
        for sel in self:
            if sel.x_pago_id:
                price = 0.00
                for line in sel.x_pago_id.lines_ids:
                    if 'Pago '+str(sel.len_cuotas)+' de' in line.name:
                        price = line.importe
                        break
                sel.precio_ultimo_pago = price

    @api.multi
    def _get_total_cursos(self):
        for sel in self:
            opciones_cursos = ('curso', 'rec', 'desc', 'inc', 'pgrado', 'diplo', 'mgrafico', 'master')
            total_cursos = 0.00
            for line in sel.order_line:
                if line.product_id.tipodecurso in opciones_cursos:
                    total_cursos += line.price_total
            sel.precio_total_curso = total_cursos

    @api.multi
    def _get_first_card(self):
        for rec in self:
            if(rec.partner_invoice_id and len(rec.partner_invoice_id.payment_token_ids)>0):
                rec.has_credit_card = self.env['payment.token'].sudo().search([
                    ('partner_id', '=', rec.partner_invoice_id.id),
                    ('active', '=', True)], limit=1) or False

    """
    Recoje los diccionarios unicamente por companyia que sean de facturas cliente A %
    ya que es el que se debe de utilizar para las automaticas.
    """
    @api.multi
    @api.depends('company_id')
    def _get_diario(self):
        """
        1 -> ISEP
        3 -> ISED
        7 -> ISED ASTURIAS
        5 -> ISED BILBAO
        4 -> ISED MADRID
        6 -> ISED Zarised
        14 -> ISEP CLINIC
        19 -> Campus ISEP MADRID
        diarios = {
                1: 1,
                3: 78,
                5: 36,
                4: 9,
                6: 57,
                14: 73,
                19: 117,
        }
        """
        for sel in self:
            if sel.company_id:
                sel.diario_id = self.env['account.journal'].sudo().search([
                    ('name', 'like', 'Facturas de cliente A%'),
                    ('company_id', '=', sel.company_id.id)
                   ], limit=1) or False


    def action_send_linea_prueba(self, id, linea):
        _logger.info('Enviando linea')
        _logger.info(self.user_id)
        _logger.info(UTF8(self.user_id.login))
        direccion = "http://ws2.aplicacion.grupoisep.com/odoo.php?"
        sql = "in_CRMUsuario=" + UTF8(str(self.user_id.login))+"&"
        sql += "in_CRMIDPedido=" + UTF8(str(id))+"&"
        if (self.partner_id.vat == 'DNI'):
            TipoDocID = 1
        else:
            TipoDocID =0
        _logger.info("AAA")
        Apellidos =str(self.partner_id.name.split(' ', 1)[1])
        Nombre = str(self.partner_id.name.split(' ', 1)[0])
        sql += "in_TipoDocID=" + UTF8(str(TipoDocID))+"&"
        sql += "in_DocID=" + UTF8(self.partner_id.vat)+"&"
        sql += "in_Apellidos=" + UTF8(Apellidos)+"&"
        sql += "in_Nombres=" + UTF8(Nombre)+"&"
        sql += "in_Sexo=" + UTF8(self.partner_id.x_sexo)+"&"
        sql += "in_FechaNacimiento=" + UTF8(str(self.partner_id.x_birthdate))+"&"
        sql += "in_Profesion=" + UTF8(self.partner_id.x_profesion)+"&"
        sql += "in_Estudios=" + UTF8(self.partner_id.x_titulacion)+"&"
        sql += "in_CentroEstudios=" + UTF8(self.partner_id.x_universidad)+"&"
        sql += "in_AnyFinalizacionEstudios=" + UTF8(str(self.partner_id.x_finalizacionestudios))+"&"
        sql += "in_Telefono=" + UTF8(str(self.partner_id.phone))+"&"
        sql += "in_Movil=" + UTF8(self.partner_id.mobile)+"&"
        sql += "in_Fax=" + UTF8(str(self.partner_id.phone))+"&"
        sql += "in_EMail=" + UTF8(self.partner_id.email)+"&"
        sql += "in_Direccion=" + str(UTF8(self.partner_id.street))+"&"
        sql += "in_Poblacion=" + str(UTF8(self.partner_id.city))+"&"
        sql += "in_CodPostal=" + UTF8(self.partner_id.zip)+"&"
        sql += "in_Provincia=" + UTF8(self.partner_id.state_id.name)+"&"
        sql += "in_Pais=" +str(UTF8(self.partner_id.country_id.name))+"&"
        sql += "in_EnvioDireccion=" + UTF8(self.partner_id.street)+"&"  # + UTF8(self.partner_id.street)+"&"
        sql += "in_EnvioPoblacion=" + str(UTF8(self.partner_id.city))+"&"  # + UTF8(self.partner_id.city)+"&"
        sql += "in_EnvioCodPostal=" + UTF8(self.partner_id.zip)+"&"  # + UTF8(self.partner_id.zip)+"&"
        sql += "in_EnvioProvincia=" + UTF8(self.partner_id.state_id.name)+"&"  # + UTF8(self.partner_id.state_id.name)+"&"
        sql += "in_EnvioPais=" + str(UTF8(self.partner_id.country_id.name))+"&"  # + UTF8(self.partner_id.country_id.name)+"&"
        sql += "in_EnvioHoraEntrega=&"
        sql += "in_CodIdentidad=" + UTF8(str(self.company_id.name))+"&"
        sql += "in_Identidad=" + UTF8(str(self.company_id.id))+"&"
        sql += "in_CRMServerPath=" + str(UTF8(self.company_id.email))+"&"
        sql += "in_CodArea=" + str(UTF8(self.opportunity_id.x_codarea))+"&"
        sql += "in_Area=" + str(UTF8(self.opportunity_id.x_area_id.name))+"&"
        sql += "in_CodTipoCurso=" + UTF8(self.opportunity_id.x_codtipodecurso)+"&"
        sql += "in_TipoCurso=" + str(UTF8(self.opportunity_id.x_tipodecurso_id.x_name))+"&"
        sql += "in_CodCurso=" + UTF8(linea.product_id.default_code)+"&"
        sql += "in_Curso=" + UTF8(linea.product_id.name)+"&"
        sql += "in_CodModalidad=" + str(UTF8(self.opportunity_id.x_modalidad_id.id))+"&"
        sql += "in_Modalidad=" + str(UTF8(self.opportunity_id.x_modalidad_id.name))+"&"
        sql += "in_CodSede=" + str(UTF8(self.opportunity_id.x_sede_id.id))+"&"
        #try:
        sql += "in_Sede=" + str(UTF8(self.opportunity_id.x_sede_id.name))+"&"
        #except ValueError:
        #   sql += "in_Sede=&"
        sql += "in_AnyAcademico=" + UTF8(str(self.x_Anyo_Academico))+"&"
        sql += "in_HorarioPreferencia=&"
        sql += "in_Observaciones=&"
        sql += "in_GrupoPreferencia=" +str(UTF8(linea.grupo_referencia))+"&"
        sql += "in_CuentaBancaria=" + str(UTF8(self.x_CCC))+"&"
        sql += "in_TarjetaCredito=" + str(UTF8(self.x_Tarjeta))+"&"
        CaducidadTarjetaCredito = str(self.x_Anyo)+str(self.x_Mes)+'01'
        try:
            datetime.strptime(CaducidadTarjetaCredito, '%Y-%m-%d')
        except ValueError:
            CaducidadTarjetaCredito = '20020101'

        sql += "in_CaducidadTarjetaCredito=" + UTF8(str.replace(str(CaducidadTarjetaCredito), "-", ""))+"&"
        sql += "in_CobroExterno=0&"
        sql += "in_PVP=0&"
        sql += "in_Descuentos=0&"
        sql += "in_Penalizacion=0&"
        sql += "in_ImporteTotalFraccionado=0&"
        sql += "in_ImporteMatricula=0&"
        sql += "in_RestoRecibos=0&"
        sql += "in_ImporteRecibos=0&"
        sql += "in_ImporteUltimoRecibo=0&"
        sql += "in_FechaPrimerRecibo=" + UTF8(str.replace(str(self.x_Fecha_Primer_Recibo), "-", ""))+"&"
        sql += "in_PagaYSenyal=0&"
        sql += "in_DeseaFactura=0&"
        sql += "in_FacturaNIF=" + UTF8(self.partner_invoice_id.vat)+"&"
        sql += "in_FacturaTitular=" + str(UTF8(self.partner_invoice_id.name))+"&"
        sql += "in_FacturaDireccion=" + UTF8(self.partner_invoice_id.street)+"&"
        sql += "in_FacturaPoblacion=" + str(UTF8(self.partner_invoice_id.city))+"&"
        sql += "in_FacturaCodPostal=" + UTF8(self.partner_invoice_id.zip)+"&"
        sql += "in_FacturaProvincia=" + UTF8(self.partner_invoice_id.state_id.name)+"&"
        sql += "in_FacturaPais=" +str(UTF8(self.partner_invoice_id.country_id.name))+"&"
        sql += "in_Pack=0"
        #_logger.info(direccion+sql)
        url= direccion+ sql
        _logger.info(url)
        direccion = "http://ws2.aplicacion.grupoisep.com/odoo.php"        
        PARAMS = {'in_CRMUsuario': UTF8(str(self.user_id.login))}
        r = requests.get(url =direccion, params=PARAMS)
        #contents = urllib.request.urlopen(url).read()
        #q = urllib.request.urlopen(url) 
        #with urllib.request.urlopen(sql) as url:
            #s = url.read()
            #_logger.info(s)

    def action_send_linea(self, id, linea):
        _logger.info('Enviando linea')
        _logger.info(self.user_id)
        _logger.info(UTF8(self.user_id.login))
        if (self.partner_id.vat == 'DNI'):
            TipoDocID = 1
        else:
            TipoDocID =0
        Apellidos =str(self.partner_id.name.split(' ', 1)[1])
        Nombre = str(self.partner_id.name.split(' ', 1)[0])
        CaducidadTarjetaCredito = str(self.x_Anyo)+str(self.x_Mes)+'01'
        if self.partner_id.x_nombre:
            Nombre = str(self.partner_id.x_nombre)
        if self.partner_id.x_apellidos:
            Apellidos = str(self.partner_id.x_apellidos)

        try:
            datetime.strptime(CaducidadTarjetaCredito, '%Y-%m-%d')
        except ValueError:
            CaducidadTarjetaCredito = '20020101'
        try:
            cpvar = int(self.partner_id.zip)
        except ValueError:
            raise ValidationError("El codigo postal del cliente debe ser un valor númerico") 
        try:
            tryvar = int(self.partner_id.x_finalizacionestudios)
        except ValueError:
            raise ValidationError("El año de finalizacion de estudios es incorrecto, debe escribir un valor númerico.")
        try:
            PARAMS = {'in_CRMUsuario': UTF8(str(self.user_id.login)),'in_CRMIDPedido': UTF8(str(id)),'in_TipoDocID' : UTF8(str(TipoDocID)),'in_DocID' : UTF8(self.partner_id.vat),'in_Apellidos' : UTF8(Apellidos), \
        'in_Nombres' : UTF8(Nombre),'in_Sexo' : UTF8(self.partner_id.x_sexo),'in_FechaNacimiento' :  UTF8(str(self.partner_id.x_birthdate)),'in_Profesion' :  UTF8(self.partner_id.x_profesion),'in_Estudios' : UTF8(self.partner_id.x_titulacion), \
        'in_CentroEstudios' :  UTF8(self.partner_id.x_universidad),'in_AnyFinalizacionEstudios' :  UTF8(str(self.partner_id.x_finalizacionestudios)),'in_Telefono' :  UTF8(str(self.partner_id.phone)),'in_Movil' :  UTF8(self.partner_id.mobile),\
        'in_Fax' :  UTF8(str(self.partner_id.phone)),'in_EMail' :  UTF8(self.partner_id.email),'in_Direccion' :  str(UTF8(self.partner_id.street)),'in_Poblacion' :  str(UTF8(self.partner_id.city)), \
        'in_CodPostal' :  UTF8(self.partner_id.zip),'in_Provincia' :  UTF8(self.partner_id.state_id.name),'in_Pais' : str(UTF8(self.partner_id.country_id.name)), 'in_EnvioDireccion' :  UTF8(self.partner_id.street), \
        'in_EnvioPoblacion' :  str(UTF8(self.partner_id.city)),'in_EnvioCodPostal' :  UTF8(self.partner_id.zip),'in_EnvioProvincia' :  UTF8(self.partner_id.state_id.name),'in_EnvioPais' :  str(UTF8(self.partner_id.country_id.name)), \
        'in_EnvioHoraEntrega':'','in_CodIdentidad' :  UTF8(str(self.company_id.name)),'in_Identidad' :  UTF8(str(self.company_id.id)),'in_CRMServerPath' :  str(UTF8(self.company_id.email)), \
        'in_CodArea' :  str(UTF8(self.opportunity_id.x_codarea)),'in_Area' :  str(UTF8(self.opportunity_id.x_area_id.name)),'in_CodTipoCurso' :  UTF8(self.opportunity_id.x_codtipodecurso), \
        'in_TipoCurso' :  str(UTF8(self.opportunity_id.x_tipodecurso_id.x_name)),'in_CodCurso' :  UTF8(linea.product_id.default_code),'in_Curso' :  UTF8(linea.product_id.name), \
        'in_CodModalidad' :  str(UTF8(self.opportunity_id.x_modalidad_id.id)),'in_Modalidad' :  str(UTF8(self.opportunity_id.x_modalidad_id.name)),'in_CodSede' :  str(UTF8(self.opportunity_id.x_sede_id.id)), \
        'in_Sede' :  str(UTF8(self.opportunity_id.x_sede_id.name)),'in_AnyAcademico' :  UTF8(str(self.x_Anyo_Academico)),'in_HorarioPreferencia' : '','in_Observaciones' : '','in_GrupoPreferencia' : str(UTF8(linea.grupo_referencia)), \
        'in_CuentaBancaria' :  str(UTF8(self.x_CCC)),'in_TarjetaCredito' :  str(UTF8(self.x_Tarjeta)),'in_CaducidadTarjetaCredito' :  UTF8(str.replace(str(CaducidadTarjetaCredito), "-", "")), \
        'in_CobroExterno' : 0,'in_PVP' : 0,'in_Descuentos' : 0,'in_Penalizacion' : 0,'in_ImporteTotalFraccionado' : 0,'in_ImporteMatricula' : 0,'in_RestoRecibos' : 0,'in_ImporteRecibos' : 0,'in_ImporteUltimoRecibo' : 0, \
        'in_FechaPrimerRecibo' :  UTF8(str.replace(str(self.x_Fecha_Primer_Recibo), "-", "")),'in_PagaYSenyal' : 0,'in_DeseaFactura' : 0,'in_FacturaNIF' :  UTF8(self.partner_invoice_id.vat), \
        'in_FacturaTitular' :  str(UTF8(self.partner_invoice_id.name)),'in_FacturaDireccion' :  UTF8(self.partner_invoice_id.street),'in_FacturaPoblacion' :  str(UTF8(self.partner_invoice_id.city)), \
        'in_FacturaCodPostal' :  UTF8(self.partner_invoice_id.zip),'in_FacturaProvincia' :  UTF8(self.partner_invoice_id.state_id.name),'in_FacturaPais' : str(UTF8(self.partner_invoice_id.country_id.name)),'in_Pack' : 0}
        #_logger.info(direccion+sql)
            direccion = "http://ws2.aplicacion.grupoisep.com/odoo.php"        
    
            r = requests.get(url =direccion, params=PARAMS)
            _logger.info("R: {}, direccion: {}, params: {}".format(r,direccion,PARAMS))
        except Exception as e:
            _logger.info(traceback.format_exc())
        #contents = urllib.request.urlopen(url).read()
        #q = urllib.request.urlopen(url) 
        #with urllib.request.urlopen(sql) as url:
            #s = url.read()
            #_logger.info(s)



    """
    Función que realiza el envio a la aplicacion.
    """
    @api.multi
    def action_send_aplicacion(self):
        self.ensure_one()
        if self.id == 0:
            return {}
        else:
            if self.partner_id:
                rerror = False
                if not self.partner_id.x_sexo:
                    rerror = True
                if not self.partner_id.x_universidad:
                    rerror = True
                if not self.partner_id.x_profesion:
                    rerror = True
                if not self.partner_id.x_tipodocumento:
                    rerror = True
                if not self.partner_id.x_titulacion:
                    rerror = True
                if not self.partner_id.x_finalizacionestudios:
                    rerror = True
                if not self.partner_id.x_birthdate:
                    rerror = True
                if not self.partner_id.x_annonacimiento:
                    rerror = True
                if rerror:
                    raise UserError(_('Los campos Sexo, Universidad, Profesión, Tipo de Documento, Titulación, Finalización de Estudios, Fecha de Nacimiento y Año Nacimiento del cliente son todos requeridos'))
                    return {}

            #self.action_invoice_create()
            #if len(self.invoice_ids) <= 0:
            #    raise UserError(_('Error en la creación de la factura'))
            if not self.x_enviado_crm:
                i=0
                for line in self.order_line:
                    _logger.info(line)
                    _logger.info(line.product_id.tipodecurso) 
                    if line.product_id.tipodecurso=='curso' or line.product_id.tipodecurso=='pgrado' or line.product_id.tipodecurso=='diplo' or line.product_id.tipodecurso=='mgrafico' or  line.product_id.tipodecurso=='master':
                        self.action_send_linea(self.id+i,line)
                        i=i+1
                    else:
                        _logger.info(line.product_id.tipodecurso) 
                #Aplicacion estos son los que valen

                self.x_enviado_crm = True

                # raise UserError(_('Enviado a la Aplicación y creada la factura'))
            return {}

    """
    Función para la generación de pagos en la tabla de isep pagos.
    Notas:
        * Todos los productos sin el campo 'tipodecurso' definido los discrimina.
        * Las lineas del plazo de pago que no sea percent o balance las discrimina.
    
    
    @api.multi
    def action_generar_pagos(self):
        for sel in self:
            if sel.x_pago_id:
                raise UserError(_('Se debe de desvincular el pago para crear uno nuevo.'))
            if not sel.payment_term_id:
                raise UserError(_('El presupuest/pedido de venta tiene que tener un plazo de pago.'))
            if not sel.x_Fecha_Primer_Recibo:
                raise UserError(_('El presupuest/pedido de venta no tiene la fecha de primer recibo.'))
            vals = {
                'name': self.env['ir.sequence'].next_by_code('isep.pagos'),
                'fecha': datetime.datetime.now(),
                'importe': sel.amount_total,
                'origin': sel.name,
            }
            total_cursos = 0.00
            bool_matricula = False
            total_matricula = 0.00
            bool_gast_env = False
            total_gast_env = 0.00
            opciones_cursos = ('curso', 'rec', 'desc', 'inc', 'pgrado', 'diplo', 'mgrafico', 'master')
            opciones_gastos_env = ('gasto_env')
            # Calculo de los importes, si el tipo del producto esta en
            # las opciones del curso entonces se le suma al total del curso
            # si es gasto de envio se pone en el total de gasto de envio
            # y si no es matricula o descuentos a esta.
            for line in sel.order_line:
                if line.product_id.tipodecurso in opciones_cursos:
                    total_cursos += line.price_total
                elif line.product_id.tipodecurso in opciones_gastos_env:
                    bool_gast_env = True
                    total_gast_env += line.price_total
                elif line.product_id.tipodecurso:
                    bool_matricula = True
                    total_matricula += line.price_total
            pago_obj = sel.env['isep.pagos'].create(vals)
            sel.x_pago_id = pago_obj
            # Creación línea Matricula
            if bool_matricula:
                vals = {
                    'pago_id': pago_obj.id,
                    'name': 'Matrícula',
                    'fecha': datetime.datetime.now(),
                    'importe': total_matricula,
                }
                sel.env['isep.pagoslineas'].create(vals)
            # Creación línea de gastos de envio
            if bool_gast_env:
                vals = {
                    'pago_id': pago_obj.id,
                    'name': 'Gastos de envio',
                    'fecha': datetime.datetime.now(),
                    'importe': total_gast_env,
                }
                sel.env['isep.pagoslineas'].create(vals)
            pago_total = len(sel.payment_term_id.line_ids)
            pago_actual = 0
            days_anteriores = None
            fecha_atenrior = None
            # Se realiza el calculo de los pagos mensuales
            for line_plazo_pago in sel.payment_term_id.line_ids.sorted(key=lambda r: r.days):
                # digito = 0.00
                pago_actual += 1
                _logger.info(sel.x_Fecha_Primer_Recibo)
                vals = {
                    'pago_id': pago_obj.id,
                    'name': 'Pago ' + str(pago_actual) + ' de ' + str(pago_total),
                    # 'fecha': datetime.datetime.now() + datetime.timedelta(days=line_plazo_pago.days),
                }
                # Se reliza la suma de dias respecto a la fecha de primer recivo
                # si utiliza un try por si da error en el mes de febrero
                try:
                    vals['fecha'] = (datetime.date(int(sel.x_Fecha_Primer_Recibo[:4]), int(sel.x_Fecha_Primer_Recibo[5:7]), int(sel.x_Fecha_Primer_Recibo[8:])) + datetime.timedelta(days=line_plazo_pago.days)).replace(day=int(sel.x_Fecha_Primer_Recibo[8:]))
                except:
                    vals['fecha'] = (datetime.date(int(sel.x_Fecha_Primer_Recibo[:4]), int(sel.x_Fecha_Primer_Recibo[5:7]), int(sel.x_Fecha_Primer_Recibo[8:])) + datetime.timedelta(days=line_plazo_pago.days)).replace(day=28)
                # Si por el aumento de dias no se tienen en cuenta que hay meses de 31 dias
                # se comprueba que la fecha anterior no sea igual a la actual calculada
                # y si lo es se suma un mes y/o un año para el calculo correcto.
                if line_plazo_pago.days != days_anteriores and line_plazo_pago.days > 0 and vals['fecha'] == fecha_atenrior:
                    if vals['fecha'].month + 1 > 12:
                        vals['fecha'] = vals['fecha'].replace(month=1)
                        vals['fecha'] = vals['fecha'].replace(year=vals['fecha'].year + 1)
                    else:
                        vals['fecha'] = vals['fecha'].replace(month=vals['fecha'].month + 1)
                days_anteriores = line_plazo_pago.days
                fecha_atenrior = vals['fecha']
                if line_plazo_pago.value == 'percent':
                    pago_parcial = round(total_cursos * line_plazo_pago.value_amount/100.0, 2)
                    if int(pago_parcial) % 5 != 0:
                        vals['importe'] = int(pago_parcial) + 5 - (int(pago_parcial) % 5)
                    else:
                        vals['importe'] = int(pago_parcial)
                elif line_plazo_pago.value == 'balance':
                    suma = 0.00
                    for item in sel.x_pago_id.lines_ids:
                        # Se suma el total de los pagos generados para realizar la diferencia con el ultimo pago.
                        if 'Pago' in item.name:
                            suma += item.importe
                    vals['importe'] = total_cursos - suma
                sel.env['isep.pagoslineas'].create(vals)
    """

    """
    bad query: b'INSERT INTO "isep_pagos" ("id", "create_uid", "create_date", "write_uid", "write_date", "fecha", "importe", "name", "origin") VALUES (nextval(\'isep_pagos_id_seq\'), 2, (now() at time zone \'UTC\'), 2, (now() at time zone \'UTC\'), \'2019-01-02 21:14:14.422073\', \'70.00\', NULL, \'SO003\') RETURNING id'
    """


    @api.multi
    def action_generar_pagos(self):
        for sel in self:
            if sel.x_pago_id:
                raise UserError(_('Se debe de desvincular el pago para crear uno nuevo.'))
            if not sel.payment_term_id:
                raise UserError(_('El presupuesto/pedido de venta tiene que tener un plazo de pago.'))
            if not sel.x_Fecha_Primer_Recibo:
                raise UserError(_('El presupuesto/pedido de venta no tiene la fecha de primer recibo.'))
            vals = {
                'name': self.env['ir.sequence'].next_by_code('isep.pagos'),
                'fecha': datetime.now(),
                'importe': sel.amount_total,
                'origin': sel.name,
            }
            total_cursos = 0.00
            bool_matricula = False
            total_matricula = 0.00
            bool_gast_env = False
            total_gast_env = 0.00
            opciones_cursos = ('curso', 'rec', 'desc', 'inc', 'pgrado', 'diplo', 'mgrafico', 'master')
            opciones_gastos_env = ('gasto_env')
            # Calculo de los importes, si el tipo del producto esta en
            # las opciones del curso entonces se le suma al total del curso
            # si es gasto de envio se pone en el total de gasto de envio
            # y si no es matricula o descuentos a esta.
            for line in sel.order_line:
                if line.product_id.tipodecurso in opciones_cursos:
                    total_cursos += line.price_total
                elif line.product_id.tipodecurso and line.product_id.tipodecurso in opciones_gastos_env:
                    bool_gast_env = True
                    total_gast_env += line.price_total
                elif line.product_id.tipodecurso:
                    bool_matricula = True
                    total_matricula += line.price_total
            pago_obj = sel.env['isep.pagos'].create(vals)
            sel.x_pago_id = pago_obj
            # Creación línea Matricula
            if bool_matricula:
                vals = {
                    'pago_id': pago_obj.id,
                    'name': 'Matrícula',
                    'fecha': datetime.now(),
                    'importe': total_matricula,
                }
                sel.env['isep.pagoslineas'].create(vals)
            # Creación línea de gastos de envio
            if bool_gast_env:
                vals = {
                    'pago_id': pago_obj.id,
                    'name': 'Gastos de envio',
                    'fecha': datetime.now(),
                    'importe': total_gast_env,
                }
                sel.env['isep.pagoslineas'].create(vals)
            pago_total = len(sel.payment_term_id.line_ids)
            pago_actual = 0
            days_anteriores = None
            fecha_atenrior = None
            # print("Fecha del pago:  -----------> "+str(sel.x_Fecha_Primer_Recibo))
            fc = sel.x_Fecha_Primer_Recibo
            dia = fc.day
            mes = fc.month
            anyo = fc.year
            #dia =int(sel.x_Fecha_Primer_Recibo[8:])
            #mes =  int(sel.x_Fecha_Primer_Recibo[5:7])
            #anyo =int(sel.x_Fecha_Primer_Recibo[:4]) 
            if (dia >=16 ):
                dia = 1
                mes = mes +1
            else:
                if (dia>=2):
                    dia=15
            if (mes >=13):
                mes=1 
                anyo=anyo+1
            _logger.debug("DIa mes año")
            
            _logger.debug(dia)
            _logger.debug(mes)
            _logger.debug(anyo)

            #Se añaden horas al datetime segun sea el caso España o Mexico
            horasañadidas = 2
            if (sel.company_id.id in [1,6]):
                horasañadidas = 8

            #fdate = datetime(anyo,mes,dia,horasañadidas)

            # Se realiza el calculo de los pagos mensuales
            for line_plazo_pago in sel.payment_term_id.line_ids.sorted(key=lambda r: r.days):
                # digito = 0.00
                pago_actual += 1
                _logger.debug("Fecha del recibo")
                _logger.debug(pago_actual)
                #_logger.debug(sel.x_Fecha_Primer_Recibo)
                #_logger.info(sel.x_Fecha_Primer_Recibo)
                vals = {
                    'pago_id': pago_obj.id,
                    'name': 'Pago ' + str(pago_actual) + ' de ' + str(pago_total),
                    # 'fecha': datetime.datetime.now() + datetime.timedelta(days=line_plazo_pago.days),
                }
                fdate = datetime(anyo, mes, dia, horasañadidas)
                # Se reliza la suma de dias respecto a la fecha de primer recivo
                # si utiliza un try por si da error en el mes de febrero
                try:
                    #fdate = datetime(anyo, mes, dia)
                    vals['fecha'] = (fdate + timedelta(days=line_plazo_pago.days)).replace(day=dia)
                    _logger.debug("TRY")
                    _logger.debug(vals['fecha'])
                    #vals['fecha'] = (datetime.date(int(sel.x_Fecha_Primer_Recibo[:4]), int(sel.x_Fecha_Primer_Recibo[5:7]), int(sel.x_Fecha_Primer_Recibo[8:])) + datetime.timedelta(days=line_plazo_pago.days)).replace(day=int(sel.x_Fecha_Primer_Recibo[8:]))
                except:
                    #fdate = datetime(anyo, mes, dia)
                    vals['fecha'] = (fdate + timedelta(days=line_plazo_pago.days)).replace(day=28)
                    _logger.debug("EXCEPT")
                    _logger.debug(vals['fecha'])
                    #vals['fecha'] = (datetime.date(int(sel.x_Fecha_Primer_Recibo[:4]), int(sel.x_Fecha_Primer_Recibo[5:7]), int(sel.x_Fecha_Primer_Recibo[8:])) + datetime.timedelta(days=line_plazo_pago.days)).replace(day=28)
                # Si por el aumento de dias no se tienen en cuenta que hay meses de 31 dias
                # se comprueba que la fecha anterior no sea igual a la actual calculada
                # y si lo es se suma un mes y/o un año para el calculo correcto.
                if line_plazo_pago.days != days_anteriores and line_plazo_pago.days > 0 and vals['fecha'] == fecha_atenrior:
                    if vals['fecha'].month + 1 > 12:
                        vals['fecha'] = vals['fecha'].replace(month=1)
                        vals['fecha'] = vals['fecha'].replace(year=vals['fecha'].year + 1)
                    else:
                        vals['fecha'] = vals['fecha'].replace(month=vals['fecha'].month + 1)
                _logger.debug(vals['fecha'])
                days_anteriores = line_plazo_pago.days
                fecha_atenrior = vals['fecha']
                if line_plazo_pago.value == 'percent':
                    pago_parcial = round(total_cursos * line_plazo_pago.value_amount/100.0, 2)
                    if int(pago_parcial) % 5 != 0:
                        vals['importe'] = int(pago_parcial) + 5 - (int(pago_parcial) % 5)
                    else:
                        vals['importe'] = int(pago_parcial)
                if line_plazo_pago.value == 'fixed':
                    vals['importe'] = line_plazo_pago.value_amount
                if line_plazo_pago.value == 'balance':
                    suma = 0.00
                    for item in sel.x_pago_id.lines_ids:
                        # Se suma el total de los pagos generados para realizar la diferencia con el ultimo pago.
                        if 'Pago' in item.name:
                            suma += item.importe
                    vals['importe'] = total_cursos - suma
                sel.env['isep.pagoslineas'].create(vals)

    """
    Se realiza una herencia para que en el momento de guardar gestione
    el producto de financiacion.
    """
    
    @api.multi
    def write(self, values):
        _logger.debug("WRITE")
        try:
            _logger.debug(values["x_Fecha_Primer_Recibo"])
            values["x_Fecha_Primer_Recibo"] =  self._change_Dia_Pago(values["x_Fecha_Primer_Recibo"])
        except:
            _logger.debug("no hay cambio")
        
        if 'amount_total' in values:
            values['x_pago_id'] = False

        result = super(sale_order, self).write(values)
        #for sel in self:
        #    sel._change_Dia_Pago()
        return result

    """
    Se realiza una herencia para que en el momento de crear gestione
    el producto de financiacion.
    """
    @api.model
    def create(self, vals):
        result = super(sale_order, self).create(vals)
        #for sel in result:
        #    sel._change_Dia_Pago()
        return result

    
    @api.one
    def _change_Dia_Pago2(self):
        hoy = datetime.date.today()
        d1 = "2018-11-15"
        date_str = '29/12/2017' # The date - 29 Dec 2017
        format_str = '%d/%m/%Y' # The format
        y = datetime.datetime.strptime(date_str, format_str)
        format_str = '%Y-%m-%d' # The format
        j = datetime.datetime.strptime(self.x_Fecha_Primer_Recibo, format_str)
        _logger.debug("_change_Dia_Pago")
        _logger.debug(self.fecha_primer_pago)
        _logger.debug(self.x_Fecha_Primer_Recibo)
        _logger.debug(hoy)
        _logger.debug(y.date())


        _logger.debug(abs(hoy - y.date()).days )
        _logger.debug(abs(hoy - j.date()).days )

        if (abs(hoy - j.date()).days>60):
            self.x_Fecha_Primer_Recibo = hoy
    @api.one
    def _change_Dia_Pago(self, fecha):
        hoy = datetime.date.today()
        format_str = '%Y-%m-%d' # The format
        j = datetime.datetime.strptime(fecha, format_str)
        _logger.debug("_change_Dia_Pago")
        _logger.debug(self.fecha_primer_pago)
        _logger.debug(fecha)
        _logger.debug(self.x_Fecha_Primer_Recibo)
        _logger.debug(hoy)


        _logger.debug(abs(hoy - j.date()).days )
        if (abs(hoy - j.date()).days>60):
            fecha =  hoy.strftime(format_str)
        dia =int(fecha[8:])
        mes =  int(fecha[5:7])
        anyo =int(fecha[:4]) 
        _logger.debug("DIa mes año")
        
        _logger.debug(dia)
        _logger.debug(mes)
        _logger.debug(anyo)
        if (dia >=16 ):
            dia = 1
            mes = mes +1
        else:
            if (dia>=2):
                dia=15
            if (mes >=13):
                mes=1 
                anyo=anyo+1
        _logger.debug(dia)
        _logger.debug(mes)
        _logger.debug(anyo) 
        _logger.debug(datetime.date(anyo, mes, dia) ) 
        return  datetime.date(anyo, mes, dia).strftime(format_str)            


    """
    Funcion que dado el total de los cursos (precios + financiacion parcialmente calculada)
    calcula la primera cuota y la ultima (dado por supuesto que las cuotas tienen el mismo %)
    y realiza el incremento que se le tendria que realizar a la financiacion para que el ultimo pago
    sea igual a los anteriores.
    """
    @api.one
    def calculo_incremento_financiacion(self, total_cursos):
        incremento = 0.0
        primer_pago = 0.0
        if len(self.payment_term_id.line_ids) > 1:
            line_plazo_pago = self.payment_term_id.line_ids.sorted(key=lambda r: r.days)[0]
            primer_pago = round(total_cursos * line_plazo_pago.value_amount/100.0, 2)
            primer_pago = int(primer_pago)
            if primer_pago % 5 != 0:
                primer_pago = int(primer_pago) + 5 - (int(primer_pago) % 5)
            incremento = primer_pago - (total_cursos - (primer_pago * (len(self.payment_term_id.line_ids)-1)))
        return incremento

    """
    Funcion que añade los recargos 1% por cada linea del plazo
    si el plazo solo tiene una linea se pone el recargo a 0
    si el plazo de pago esta sin asignar se borra el recargo
    para todo lo demas mastercad :D
    """
    @api.one
    def _change_payment_term_id(self):
        if self.payment_term_id:
            opciones_cursos = ('curso', 'rec', 'desc', 'inc', 'pgrado', 'diplo', 'mgrafico', 'master')
            # Calculo de los importes, si el tipo del producto esta en
            # las opciones del curso entonces se le suma al total del curso
            # si es gasto de envio se pone en el total de gasto de envio
            # y si no es matricula o descuentos a esta.
            total_cursos = 0.00
            encontrado = False
            for line in self.order_line:
                if "Financiaci" in line.name:
                    encontrado = True
                if line.product_id.tipodecurso in opciones_cursos and 'Financiaci' not in line.name:
                    total_cursos += line.price_total
            if not encontrado:
                product_obj = self.env.ref('isep_custom.product_isep_recargo')
                product_uom_id = self.env['product.uom'].search([('name', 'like', 'Uni%')]).id
                vals = {
                    'pricelist': self.pricelist_id.id,
                    'product_id': product_obj.id,
                    'qty': 1.0,
                    'product_uom': product_uom_id,
                    'product_uos': product_uom_id,
                    'product_uom_qty': 1.0,
                    'qty_uos': 1.0,
                    'partner_id': self.env.user.id,
                    'state': 'draft',
                    'name': product_obj.product_tmpl_id.name,
                    'price_unit': 0.00,
                    'order_id': self.id,
                }
                if len(self.payment_term_id.line_ids) > 1:
                    vals['price_unit'] = total_cursos * (len(self.payment_term_id.line_ids)*0.5)/100.0
                    total_cursos += vals['price_unit']
                    vals['price_unit'] += self.calculo_incremento_financiacion(total_cursos)[0]
                vals.update(self.sudo().env['sale.order.line'].product_id_change())
                self.sudo().env['sale.order.line'].create(vals)
            else:
                for line in self.order_line:
                    if "Financiaci" in line.name:
                        if len(self.payment_term_id.line_ids) > 1:
                            precio = total_cursos * (len(self.payment_term_id.line_ids)*0.5)/100.0
                            total_cursos += precio
                            line.price_unit = precio + self.calculo_incremento_financiacion(total_cursos)[0]
                        else:
                            line.price_unit = 0.00
        else:
            for line in self.order_line:
                if "Financiaci" in line.name:
                    line.unlink()

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        for sel in self:
            if not sel.x_pago_id and sel.curso:
                raise ValidationError(_("No se puede crear la factura sin la previa generación de pagos!."))
        super(sale_order, self).action_invoice_create(grouped, final)
        #for order in self:
        #    if order.curso and len(order.invoice_ids) == 1:
        #        if order.diario_id:
        #            order.invoice_ids.journal_id = order.diario_id 
        #        else:
        #            raise ValidationError(_("Hay un error con el diario en ventas.")) 

    @api.multi
    def action_confirm(self):
        for sel in self:
            sel.partner_id.customer = True
            sel.partner_invoice_id.customer = True
            text_error = ''
            if not sel.partner_id.vat and sel.company_id == 1111:
                text_error += "No se puede confirmar si el cliente no tiene RFC.\n"
            if not sel.x_Matricula_Pagada:
                text_error += "No se ha pagado la matrícula.\n"
            #if sel.payment_mode_id_name == 'Datáfono' and not sel.tarjeta_credito:
                #text_error += "No se ha seleccionado una tarjeta de crédito.\n"
            if sel.payment_mode_id_name == 'Domiciliado' and not sel.cuenta_bancaria:
                text_error += "No se ha seleccionado una cuenta bancaria.\n"
            if sel.payment_mode_id_name == 'Domiciliado' and not sel.mandate_id:
                text_error += "No se ha seleccionado un mandato bancario.\n"
            if not sel.payment_mode_id:
                text_error += "No se ha seleccionado un modo de pago.\n"
            if not self.partner_id.country_id:
                text_error += "No se ha seleccionado un país para este cliente.\n"
            if sel.company_id.id == 1:
                if "tarjeta" in str(sel.payment_mode_id.name).lower() and not self.partner_invoice_id.payment_token_ids:
                    text_error += "No se puede confirmar el pedido si la forma de pago es tarjeta y el cliente no tiene asociada una tarjeta de credito.\n"
                if "conta" not in str(sel.pricelist_id.name).lower():
                    if not sel.x_pago_id:
                        text_error += "Si la tarifa de pago no es a contado debe haber un pago asociado, hacer click en generar pagos para hacerlo.\n"
                    if "transfer" in str(sel.payment_mode_id.name).lower():
                        text_error += "Si la tarifa de pago no es a contado, la forma de pago no puede ser transferencia.\n"
            if text_error != '':
                raise ValidationError(text_error)
        res = super(sale_order, self).action_confirm()
        return res

    """
    Constrain que si el importe del pedido de venta no es igual que el
    total de los pagos elimina el pago.
    """
    @api.multi
    @api.constrains('amount_total')
    def cons_pago_amount_total(self):
        for sel in self:
            if sel.x_pago_id and sel.amount_total != sel.x_pago_id.importe:
                sel.x_pago_id = None

    """
    Constrain que determina las lineas de pago con las lineas del payment term
    si no tienen equivalencia, borra el pago.
    """
    @api.multi
    @api.constrains('payment_term_id')
    def cons_pago_payment_term(self):
        for sel in self:
            if sel.x_pago_id:
                if not sel.payment_term_id:
                    sel.x_pago_id = None
                else:
                    line = len(self.env['isep.pagoslineas'].search([
                        ('name', 'like', 'Pago %'),
                        ('id', '=', sel.x_pago_id.id)
                        ]))
                    if len(sel.payment_term_id.line_ids) != line:
                        sel.x_pago_id = None

    """
    Proceso de creacion de tarjetas de credito
    y lo asigna al pedido de venta
    """
    def _crear_tarjeta_credito(self, company_id):
        vals_tarjeta = {
            'partner_id': self.partner_invoice_id.id,
            'acquirer_id': self.env['payment.acquirer'].search([
                ('name', 'like', 'Datafono'),
                ('company_id', '=', company_id)
                ])[0].id,
            'name': self.partner_invoice_id.name,
            'acquirer_ref': self.x_Tarjeta.replace(' ', ''),
            'csv': self.x_CVC or None,
        }
        if self.x_Mes and self.x_Anyo:
            year = int(self.x_Anyo)
            if year < 100:
                year += 2000
            vals_tarjeta['caducidad'] = datetime.date.today().replace(year=year).replace(month=int(self.x_Mes)).replace(day=1)
        tarjeta_obj = self.env['account.payment.method'].create(vals_tarjeta)
        self.tarjeta_credito = tarjeta_obj.id

    """
    Proceso de creacion de cuentas bancarias y su mandato validado
    y lo asigna al pedido de venta
    """
    def _crear_cuenta_bancaria(self, company_id):
        vals_ccc = {
            'acc_number': self.x_CCC,
            'partner_id': self.partner_invoice_id.id,
            'company_id': company_id,
        }
        cuenta_obj = self.env['res.partner.bank'].create(vals_ccc)
        vals_mandate = {
                        'company_id': company_id,
                        'type': 'recurrent',
                        'recurrent_sequence_type': 'recurring',
                        'scheme': 'CORE',
                        'format': 'sepa',
                        'signature_date': datetime.date.today().replace(day=1).replace(month=9),
                        'partner_bank_id': cuenta_obj.id
                    }
        mandate_obj = self.env['account.banking.mandate'].create(vals_mandate)
        mandate_obj.validate()
        self.cuenta_bancaria = cuenta_obj.id

    """
    Proceso que crea las cuentas bancarias y tarjetas de credito
    sobre los pedidos validados que están en los campos antiguos
    """
    @api.model
    def creacion_ccc_tc_pedidos_venta(self):
        _logger.info('-->>> Empiezo creacion_ccc_tc_pedidos_venta')
        for company in self.env['res.company'].search([]):
            _logger.info("Empresa")
            _logger.info(company.name)
            for sale_order in self.env['sale.order'].search([
                    ('company_id', '=', company.id),
                    ('state', 'in', ('done', 'sale'))
                    ]):
                _logger.info(sale_order.name)
                if sale_order.x_CCC and len(sale_order.x_CCC) > 4:
                    if not self.env['res.partner.bank'].search([
                        ('partner_id', '=', sale_order.partner_invoice_id.id),
                        ('company_id', '=', company.id)
                    ]):
                        sale_order._crear_cuenta_bancaria(company.id)
                        _logger.info("<<-- CREO CCC")
                if sale_order.x_Tarjeta and len(sale_order.x_Tarjeta) > 4:
                    if not self.env['account.payment.method'].search([
                        ('partner_id', '=', sale_order.partner_invoice_id.id),
                        ('acquirer_ref', '=', sale_order.x_Tarjeta.replace(' ', ''))
                            ]):
                        sale_order._crear_tarjeta_credito(company.id)
                        _logger.info("<<-- CREO TARJETA")
