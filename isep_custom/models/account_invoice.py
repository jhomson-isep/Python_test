# -*- coding: utf-8 -*-

import logging
from openerp import api, fields, models, _
from openerp.exceptions import UserError
import datetime
from odoo.tools import float_is_zero, float_compare
_logger = logging.getLogger(__name__)


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    x_Titular_Factura = fields.Char(string="Titular Factura")
    x_Tarjeta = fields.Char(string="Tarjeta de Crédito")
    x_Recibo_Forma_Pago = fields.Many2one('payment.acquirer', string="Forma de Pago de los Recibos")
    x_Paga_y_Senyal_Vencimiento = fields.Date(string="Fecha de Vencimiento de la Paga y Señal")
    x_Paga_y_Senyal_Pagada = fields.Boolean(string="Paga y Señal Pagada")
    x_Paga_y_Senyal_Fecha_Pago = fields.Date(string="Fecha de Pago de la Paga y Señal")
    x_Paga_y_Senyal = fields.Monetary(string="paga y Señal")
    x_Mes = fields.Integer(string="Mes")
    x_Matricula_Vencimiento = fields.Date(string="Fecha de Vencimiento de la Matrícula")
    x_Matricula_Pagada = fields.Boolean(string="Matrícula Pagada")
    x_Matricula_Forma_Pago = fields.Many2one('payment.acquirer', string="Forma de Pago de la Matrícula")
    x_Matricula_Fecha_Pago = fields.Date(string="Fecha de Pago de la Matrícula")
    x_GrupoReferencia = fields.Char(string="Grupo de Referencia")
    x_Desea_Factura = fields.Boolean(string="Desea Factura")
    x_CVC = fields.Char(string="Código CVC")
    x_CCC = fields.Char(string="Cuenta Bancaria")
    x_Anyo = fields.Integer(string="Año")
    sale_order_ids = fields.Many2many('sale.order', compute='compute_sale_orders')
    prorata_financiacion_lineas = fields.Integer(string="prorrata de la financiacion", compute="_get_prorata_financiacion_lineas")
    #mail_to_factura_validada = fields.Char(string="Cuenta de Mail para el mail atomatico", compute="_get_mail_to_factura_validada") 
    name_to_factura_validada = fields.Char(string="Nombre para el mail atomatico", compute="_get_name_to_factura_validada")
    mensualidad = fields.Float(string="Mensualidad", compute="_get_mensualidad")

    """
    Funcion que calcula el precio de la proxima mensualidad a pagar
    por el alumno.
    """
    @api.multi
    def _get_mensualidad(self):
        for sel in self:
            total = 0.0
            if sel.move_id:
                for line in sel.move_id.line_ids.sorted(key=lambda r: r.date_maturity).filtered(lambda r: r.account_id.code == '430000'):
                    if total == 0.0 and not line.reconciled:
                        total = line.debit
            sel.mensualidad = total

    """
    Funcion que indica el correo electronico para el mail automatico
    de validacion de facturas.
    """
    @api.multi
    def _get_mail_to_factura_validada(self):
        _logger.info("----------------------------------------------------------")
        _logger.info("Recoge el mail para la factuar")
        _logger.info("----------------------------------------------------------")
        for sel in self:
            if 'ISEP' in sel.company_id.name:
                if 'LATAM' in sel.company_id.name:
                    sel.mail_to_factura_validada = "mexico@grupoisep.com"
                else:
                    sel.mail_to_factura_validada = "ollorente@grupoisep.com"
            else:
                sel.mail_to_factura_validada =  "nmolina@grupoisep.com"

    @api.multi
    def _get_name_to_factura_validada(self):
        for sel in self:
            if 'ISEP' in sel.company_id.name:
                if 'LATAM' in sel.company_id.name:
                    sel.name_to_factura_validada = "México"
                else:
                    sel.name_to_factura_validada = "Oscar"
            else:
                sel.name_to_factura_validada = "Noemi"
    group_tax_line = fields.One2many('temp.tax', 'id_factura', string='Tax Lines')

    """
    Funcion que facilita el calculo de la distribucion de la financiacion
    en el calculo de las lineas de la factura para la impresion del report.
    _get_price_unit_report
    """
    @api.multi
    def _get_prorata_financiacion_lineas(self):
        opciones_cursos = ('curso', 'pgrado', 'diplo', 'mgrafico', 'master')
        for sel in self:
            total_cursos = 0.0
            total_finan = 0.0
            for line in sel.invoice_line_ids:
                if line.product_id.tipodecurso in opciones_cursos:
                    total_cursos += 1
                if 'Financiaci' in line.name:
                    total_finan += line.price_subtotal
            if total_cursos > 0:
                sel.prorata_financiacion_lineas = total_finan/total_cursos
            else:
                sel.prorata_financiacion_lineas = 0.0

    """
    Esta funcion recorre las lineas de la factura
    para mapear el campo invoice_lines de sale order line
    con el de las lineas de la factura para asi coger
    todas las sale orders asociadas a la factura
    """
    @api.multi
    def compute_sale_orders(self):
        for sel in self:
            sel.sale_order_ids = self.env['sale.order.line'].search(
                [('invoice_lines', 'in', sel.invoice_line_ids.ids)]).mapped(
                'order_id')

    """
    Se realiza una herencia para que no se pueda borrar una factura
    que ya ha sido validada.
    """
    @api.multi
    def unlink(self):
        for invoice in self:
            if invoice.number:
                raise UserError(_('No puede borrar una factura que ya ha sido validada. Debería abonarla en su lugar.'))
        return super(account_invoice, self).unlink()

    """
    Función que poner por defecto un mandato y una cuenta bancaria
    cuando el campo mandate_required es True.
    """
    @api.multi
    @api.onchange('mandate_required')
    def onchange_mandate_required(self):
        for sel in self:
            if sel.mandate_required:
                if sel.company_id and sel.company_id.partner_id:
                    sel.partner_bank_id = self.env['res.partner.bank'].search([
                        ('company_id', '=', sel.company_id.id), 
                        ('partner_id', '=', sel.company_id.partner_id.id)
                        ], limit=1)
                if sel.commercial_partner_id:
                    sel.mandate_id = self.env['account.banking.mandate'].search([
                        ('partner_id', '=', sel.commercial_partner_id.id),
                        ('company_id', '=', sel.company_id.id),
                        ('state', '=', 'valid')
                        ], limit=1)
            else:
                sel.partner_bank_id = None
                sel.mandate_id = None

    """
    Funciones:
    * Desconcilia el asiento de la factura.
    * Busca si tiene la factura una matricula y gastos de envio asociados.
    * Si la tiene realiza una busqueda en el modo de pago del importe
        para asociar la busqueda.
    * Se recorren las lineas del asiento de las cuentas 430000 debido que
        son las que se le cobrarán al cliente y se asocian los precios y
        las fechas de vencimientos de la tabla isep_pagoslineas asociados
        a la sale order.
    * Se publica el asiento.
    """
    
    def _change_account_move_price(self):
        if self.move_id:
            invoice_currency = self.currency_id or False
            company_currency = self.company_id.currency_id or False
            bsamecurrency = invoice_currency == company_currency
            _logger.warning("----->>>>> ACOUNT MOVE LINE")
            # Cancelamos el asiento
            self.move_id.button_cancel()
            if self.move_id.state == "draft":
                self.move_id.partner_id = self.partner_id.id
                opciones_cursos = ('curso', 'rec', 'desc', 'inc', 'pgrado', 'diplo', 'mgrafico', 'master')
                bool_matricula = False
                bool_gasto_envio = False
                for line in self.sale_order_ids[0].order_line:
                    if line.product_id.tipodecurso == 'gasto_env':
                        bool_gasto_envio = True
                    elif line.product_id.tipodecurso not in opciones_cursos:
                        bool_matricula = True
                pagos_objs = self.sale_order_ids.x_pago_id.lines_ids.sorted(key=lambda r: r.fecha)
                pagos_recorridos = 0
                # Se realiazan los cambios de la matricula y de los gastos de envio debido a que
                # serán los primeros pagos y se duplican lineas debido a que el sistema no lo genera.
                for line_obj in self.move_id.line_ids.sorted(key=lambda r: r.date_maturity):
                    line_obj.partner_id = self.partner_id.id
                    if (line_obj.account_id.code == '430000' and self.company_id.id == 1) or (
                            line_obj.account_id.code[:6] == '105-00' and self.company_id.id in [1, 1111]):
                        if bool_matricula:
                            line_matricula = line_obj.with_context(check_move_validity=False).copy()
                            line_matricula.name = pagos_objs[pagos_recorridos].name
                            line_matricula.date_maturity = pagos_objs[pagos_recorridos].fecha.date()#datetime.datetime.strptime(pagos_objs[pagos_recorridos].fecha.split(" ")[0], '%Y-%m-%d')

                            line_matricula.with_context(check_move_validity=False).debit = pagos_objs[pagos_recorridos].importe
                            #_logger.debug("MatrApunt id {} monto{}".format(line_matricula.id, line_matricula.debit))
                            if not bsamecurrency:
                                line_matricula.with_context(check_move_validity=False).debit = pagos_objs[pagos_recorridos].importe * invoice_currency.rate2
                                line_matricula.amount_currency = pagos_objs[pagos_recorridos].importe
                            bool_matricula = False
                            pagos_recorridos += 1
                            _logger.debug("MatrApunte id {} monto {}".format(line_matricula.id, line_matricula.debit))
                        if bool_gasto_envio:
                            line_matricula = line_obj.with_context(check_move_validity=False).copy()
                            line_matricula.name = pagos_objs[pagos_recorridos].name
                            line_matricula.date_maturity = pagos_objs[pagos_recorridos].fecha.date()#datetime.datetime.strptime(pagos_objs[pagos_recorridos].fecha.split(" ")[0], '%Y-%m-%d')
                            line_matricula.debit = pagos_objs[pagos_recorridos].importe
                            if not bsamecurrency:
                                line_matricula.debit = pagos_objs[pagos_recorridos].importe * invoice_currency.rate2
                                line_matricula.amount_currency = pagos_objs[pagos_recorridos].importe
                            bool_gasto_envio = False
                            pagos_recorridos += 1
                        line_obj.name = pagos_objs[pagos_recorridos].name
                        line_obj.date_maturity = pagos_objs[pagos_recorridos].fecha.date()#datetime.datetime.strptime(pagos_objs[pagos_recorridos].fecha.split(" ")[0], '%Y-%m-%d')
                        line_obj.with_context(check_move_validity=False).debit = pagos_objs[pagos_recorridos].importe
                        if not bsamecurrency:
                                line_obj.with_context(check_move_validity=False).debit = pagos_objs[pagos_recorridos].importe * invoice_currency.rate2
                                line_obj.with_context(check_move_validity=False).amount_currency = pagos_objs[pagos_recorridos].importe
                        #_logger.debug("Apunte id {} monto {} moneda {}".format(line_obj.id, line_obj.debit, line_obj.amount_currency))

                        pagos_recorridos += 1
                if not bsamecurrency:
                    self.check_difference_currency()
                    #if line_obj.credit > 0.0:
                    #    _logger.debug("Apunte id {} credito {} moneda{}".format(line_obj.id, line_obj.credit, line_obj.amount_currency))
            # Publicamos el asiento
            self.move_id.post()
        else:
            raise UserError(_('No se ha creado el Asiento.'))
        # raise UserError(_('Fallo adrede.'))
        
    """Función que añade la diferencia producida por la conversion de moneda al ultimo apunte.
       Se valida que la diferencia no sea mayor que la definida por la misma moneda con float_is_zero.
       ----------------------------------------------------------------------------------------------
    """
    def check_difference_currency(self):
        suma_debit = 0.0
        suma_credit = 0.0
        mayorcredit = 0
        tempmc = 0.0
        rounding = self.company_id.currency_id.rounding
        for line_obj in self.move_id.line_ids.sorted(key=lambda r: r.date_maturity):
            if line_obj.credit == 0.0:
                suma_debit += line_obj.debit
            if line_obj.debit == 0.0:
                suma_credit += line_obj.credit
                if line_obj.credit > tempmc:
                    tempmc = line_obj.credit
                    mayorcredit = line_obj.id
        #_logger.debug("Debito {} Credito {} mayorcreditoid {}".format(suma_debit, suma_credit, mayorcredit))
        #_logger.debug("float is zero {}".format(float_is_zero(abs(suma_credit - suma_debit), rounding)))
        if suma_credit != suma_debit and float_is_zero(abs(suma_credit - suma_debit), rounding) :
            line_obj = self.move_id.line_ids.filtered(lambda r: r.id == mayorcredit)[0]
            suma = suma_debit - suma_credit
            line_obj.with_context(check_move_validity=False).credit += suma
            #_logger.debug("Suma {}, credito final {}".format(suma, line_obj.credit))

    """
    Se hereda la funcion para controlar que:
    * La factura viene de una unica sale order
    * El sale order tiene el checkbox de curso activado
    * El sale order tiene el pago creado
    para despues cambiar las lineas del asiento para
    adecuarlas la pago creado por el archivo gmri
    """
    
    @api.multi
    def action_move_create(self):
        res = super(account_invoice, self).action_move_create()
        _logger.warning("----->>>>> action_move_create")
        for sel in self:
            if len(sel.sale_order_ids) == 1:
                if sel.sale_order_ids.curso:
                    if sel.sale_order_ids.x_pago_id:
                        sel._change_account_move_price()
                    else:
                        raise UserError(_('La orden de venta no tiene creado el pago.'))
            if sel.type in ('out_refund', 'out_invoice') and sel.payment_mode_id.name and 'Dat' in sel.payment_mode_id.name:
                _logger.warning("pasamos a enviar el mensaje")
                template_browse = self.env['mail.template'].browse(200000010)
                template_browse.send_mail(sel.id, force_send=True)
        return res
        

    """
    Se crea una tabla intermedia entre account invoice y account invoice tax.
    En esta tabla se guarda una agrupación de las tasas con el mismo nombre.
    Sólo se recalculan las tasas al editar o crear facturas.
    """
    @api.multi
    def get_group_tax_line(self):
        for sel in self:
            tax_dict = {}
            for tax in sel.tax_line_ids:
                if tax not in tax_dict:
                    tax_dict[tax.name] = {}
                    tax_dict[tax.name]['amount'] = tax.amount
                    tax_dict[tax.name]['base'] = tax.base
                else:
                    tax_dict[tax.name]['amount'] += tax.amount
            temp_tax = self.env['temp.tax']
            for obj in temp_tax.search([('id_factura', '=', sel.id)]):
                obj.unlink()
            for tax in tax_dict:
                temp_tax.create({
                        'name': tax,
                        'amount': tax_dict[tax]['amount'],
                        'base': tax_dict[tax]['base'],
                        'id_factura': sel.id
                    })

    @api.model
    def create(self, values):
        res = super(account_invoice, self).create(values)
        for r in res:
            r.get_group_tax_line()
        return res

    @api.multi
    def write(self, values):

        res = super(account_invoice, self).write(values)
        for sel in self:
            sel.get_group_tax_line()
        return res

    """
    Funcion que revisa las facturas creadas de clientes y
    actualiza el modo de pago y lo correspondiente si no tiene
    y esta indicado en el pedido de venta relacionado y comprueba
    que todos los efectos(apuntes) tengan el modo de pago y el cliente
    y cambia el dia de vencimiento a 1 < 15 y a 15 > 15.
    """

    @api.model
    def actualizacion_datos_efectos(self):
        _logger.info('--->>>>>>>>> actualizacion_datos_efectos')
        modos_pago_pedido_vent = {
            1: "Transferencia",  # transferencia
            2: "Dat%",  # datafono
            4: "Efectivo",  # efectivo
            7: "Domiciliado",  # Domiciliado
        }
        for company in self.env['res.company'].search([]):
            modo_de_pago_falta = []  # contiene apuntes
            mandato_cliente_falta = []  # contiene clientes
            for factura in self.env['account.invoice'].search([
                    ('type', '=', 'out_invoice'),
                    ('company_id', '=', company.id)
                    ]):
                if factura.move_id:
                    # Cancelamos el asiento
                    factura.move_id.button_cancel()
                    if not factura.move_id.partner_id:
                        factura.move_id.partner_id = factura.partner_id.id
                    for apunte in factura.move_id.line_ids:
                        if not apunte.partner_id:
                            apunte.partner_id = factura.partner_id.id
                        if not apunte.payment_mode_id:
                            if factura.payment_mode_id:
                                apunte.payment_mode_id = factura.payment_mode_id.id
                            else:
                                for pedido_venta in factura.sale_order_ids:
                                    if pedido_venta.x_Recibo_Forma_Pago:
                                        apunte.payment_mode_id = self.env['account.payment.mode'].search([
                                            ('name', 'like', modos_pago_pedido_vent[pedido_venta.x_Recibo_Forma_Pago.id]),
                                            ('company_id', '=', company.id)
                                            ])[0].id
                            if not apunte.payment_mode_id:
                                modo_de_pago_falta.append([apunte.id, apunte.name])
                        if apunte.account_id.code == '430000':
                            if apunte.payment_mode_id and 'Domiciliado' in apunte.payment_mode_id.name:
                                if not apunte.mandate_id:
                                    if factura.mandate_id:
                                        apunte.mandate_id = factura.mandate_id.id
                                    else:
                                        mandate_obj = self.env['account.banking.mandate'].search([
                                                ('partner_id', '=', factura.partner_id.id),
                                                ('company_id', '=', company.id)
                                                ])
                                        if mandate_obj:
                                            apunte.mandate_id = mandate_obj[0].id
                                if not apunte.mandate_id:
                                    mandato_cliente_falta.append([factura.partner_id.id, factura.partner_id.name])
                            if apunte.date_maturity:
                                dia_vencimiento = 1
                                if int(apunte.date_maturity[8:10]) >= 15:
                                    dia_vencimiento = 15
                                apunte.date_maturity = datetime.date(int(apunte.date_maturity[:4]), int(apunte.date_maturity[5:7]), dia_vencimiento)
                    _logger.info(factura.move_id)
                    # Publicamos el asiento
                    factura.move_id.post()
            _logger.info('--->>>>>>>>> DATOS QUE FALTAN')
            _logger.info(company.name)
            _logger.info(modo_de_pago_falta)
            _logger.info(mandato_cliente_falta)

    @api.model
    def _actualizacion_datos_efectos_mexico(self):
        _logger.info('--->>>>>>>>> actualizacion_datos_efectos_mexico')
        modos_pago_pedido_vent = {
            1: "Transferencia",  # transferencia
            2: "Dat%",  # datafono
            4: "Efectivo",  # efectivo
            7: "Domiciliado",  # Domiciliado
        }

        casosanormalizar = []
        for company in self.env['res.company'].search([]):
            modo_de_pago_falta = []  # contiene apuntes
            mandato_cliente_falta = []  # contiene clientes
            for factura in self.env['account.invoice'].search([
                    ('type', '=', 'out_invoice'),
                    ('company_id', '=', company.id)
                    ]):
                _logger.debug("---Factura nueva:")
                _logger.debug(factura.id)
                if(factura.create_date.date() >= datetime.date.today()):
                    _logger.debug("Factura {} omitida".format(factura.id))
                    continue
                pagos_objs = factura.sale_order_ids.x_pago_id.lines_ids.sorted(key=lambda r: r.fecha) or False
                if pagos_objs:
                    _logger.debug("Tiene pagos")
                else:
                    _logger.debug("No tiene pagos")
                fecha_vencimiento = factura.sale_order_ids.x_Fecha_Primer_Recibo or False

                opciones_cursos = ('curso', 'rec', 'desc', 'inc', 'pgrado', 'diplo', 'mgrafico', 'master')
                bool_matricula = False
                bool_gasto_envio = False
                precio_matricula = 0.0

                if self.sale_order_ids:
                    for line in self.sale_order_ids[0].order_line:
                        if line.product_id.tipodecurso == 'gasto_env':
                            bool_gasto_envio = True
                        elif line.product_id.tipodecurso not in opciones_cursos:
                            bool_matricula = True
                            precio_matricula= line.price_subtotal

                
                if factura.move_id:# and pagos_objs and fecha_vencimiento:
                    fechatiene = False
                    tienepedidos = "No tiene pedidos"
                    if pagos_objs:
                        tienepedidos = "Si tiene pedidos"
                    dia_vencimiento = 1
                    if fecha_vencimiento:
                        dia_vencimiento = int(fecha_vencimiento.day)                 
                        fechatiene = True


                    _logger.debug("factura {} Dia vencimiento {} {}".format(factura.id, dia_vencimiento, tienepedidos))
                    #_logger.debug(dia_vencimiento)
                    monthplusone = False

                    if (dia_vencimiento >= 16):
                        dia_vencimiento = 1
                        monthplusone = True
                    #elif (dia_vencimiento == 2):
                    #    dia_vencimiento = 1
                    elif (dia_vencimiento in range(2,16)):
                        dia_vencimiento = 15



                    _logger.debug("Diaa modif")
                    _logger.debug(dia_vencimiento)
                    # Cancelamos el asiento
                    factura.move_id.button_cancel()
                    if not factura.move_id.partner_id:
                        factura.move_id.partner_id = factura.partner_id.id
                    if pagos_objs:
                        apuntespagos = len(factura.move_id.line_ids.filtered(lambda r: r.debit > 0))
                        if(apuntespagos != len(pagos_objs)):
                            _logger.debug("este se normaliza fcatura {} asiento {}".format(factura.id, factura.move_id))
                            casosanormalizar.append(factura.move_id)
                    primerap = True
                    ffa = False
                    for apunte in factura.move_id.line_ids.sorted(key=lambda r: r.date_maturity):
                        #if(bool_matricula):
                        #    if(apunte.debit != precio_matricula):
                        #        casosanormalizar.append(factura.move_id)
                        #        break
                        #    bool_matricula = False
                        #    continue
                        #monthplusone = monthplusone or int(apunte.date_maturity[5:7])>=16
                        if not apunte.partner_id:
                            apunte.partner_id = factura.partner_id.id
                        if not apunte.payment_mode_id:
                            if factura.payment_mode_id:
                                apunte.payment_mode_id = factura.payment_mode_id.id
                            else:
                                for pedido_venta in factura.sale_order_ids:
                                    if pedido_venta.x_Recibo_Forma_Pago:
                                        apunte.payment_mode_id = self.env['account.payment.mode'].search([
                                            ('name', 'like', modos_pago_pedido_vent[pedido_venta.x_Recibo_Forma_Pago.id]),
                                            ('company_id', '=', company.id)
                                            ])[0].id
                            if not apunte.payment_mode_id:
                                modo_de_pago_falta.append([apunte.id, apunte.name])
                        if (company.id == 1 and apunte.credit == 0):# and factura.create_date < datetime.date.today()):
                            #(apunte.account_id.code == '430000' and company.id == 6) or (apunte.account_id.code[:6] == '105-00' and company.id == 1):
                            #_logger.debug("Entro a la edicion")
                            #_logger.debug("SxS")

                            if apunte.payment_mode_id and 'Domiciliado' in apunte.payment_mode_id.name:
                                if not apunte.mandate_id:
                                    if factura.mandate_id:
                                        apunte.mandate_id = factura.mandate_id.id
                                    else:
                                        mandate_obj = self.env['account.banking.mandate'].search([
                                                ('partner_id', '=', factura.partner_id.id),
                                                ('company_id', '=', company.id)
                                                ])
                                        if mandate_obj:
                                            apunte.mandate_id = mandate_obj[0].id
                                if not apunte.mandate_id:
                                    mandato_cliente_falta.append([factura.partner_id.id, factura.partner_id.name])
                            #ffa = False
                            if (apunte.date_maturity and "Matr" not in apunte.name and factura.create_date.date() != apunte.date_maturity and apunte.date_maturity > datetime.date.today()):
                                _logger.debug("-----Apunte nuevo fecha:")
                                _logger.debug("Apunte {}, fecha: {} ".format(apunte.id,  apunte.date_maturity))

                                if(int(apunte.date_maturity.day) in (15,1)):
                                    _logger.debug("Ya tiene fecha correcta factura {} apunte {} asiento {} fecha recibos {}".format(factura.id,factura.move_id.id,apunte.id,apunte.date_maturity))
                                    if primerap:
                                        break
                                    
                                if not fechatiene:
                                    diauno = int(apunte.date_maturity.day) or 0
                                    if (diauno >= 16):
                                        dia_vencimiento = 1
                                        monthplusone = True
                                    #elif (dia_vencimiento == 2):
                                    #    dia_vencimiento = 1
                                    elif (diauno in range(2,16)):
                                        dia_vencimiento = 15
                                    elif diauno==0:
                                        _logger.debug("Dia igual a o, nothing to do")
                                        continue

                                #dia_vencimiento = 1
                                mes = int(apunte.date_maturity.month)+1 if (monthplusone) else int(apunte.date_maturity.month)
                                anyo = int(apunte.date_maturity.year)
                                if (mes > 12):
                                    mes = 1
                                    anyo = int(apunte.date_maturity.year) +1 
                                fecha_tentativa = datetime.date(anyo, mes, dia_vencimiento)
                                if(fecha_tentativa<apunte.date_maturity):
                                    mes = mes + 1
                                    if(mes>12):
                                        mes = 1
                                        anyo = anyo + 1
                                    fecha_tentativa = datetime.date(anyo, mes, dia_vencimiento)
                                monthplusone = False

                                #ffa
                                
                                if(ffa):#echa_anterior):
                                    if(fecha_anterior == fecha_tentativa):
                                        mes = mes + 1
                                        if(mes>12):
                                            anyo = anyo + 1
                                        fecha_tentativa = datetime.date(anyo, mes, dia_vencimiento)
                                '''
                                    monthplusone = False
                                    diferencia = fecha_tentativa - fecha_anterior
                                    if(diferencia > timedelta(days=20)):
                                        apunte.date_maturity = fecha_tentativa
                                    else:
                                        #mes = monthplusone?int(apunte.date_maturity[5:7])int(apunte.date_maturity[5:7]) + 1
                                        if(mes > 12):
                                            mes = 1
                                            anyo = int(apunte.date_maturity[:4]) + 1
                                            fecha_tentativa = datetime.date(dia_vencimiento, mes, anyo)
                                        else:
                                            fecha_tentativa = datetime.date(dia_vencimiento, mes, int(apunte.date_maturity[:4]))
                                if int(apunte.date_maturity[8:10]) >= 15:
                                    dia_vencimiento = 15
                                '''
                                _logger.debug("Fecha apunte")
                                _logger.debug("Apunte id: %s, fecha: %s", str(apunte.id), str(fecha_tentativa))
                                primerap = False
                                apunte.date_maturity = fecha_tentativa #datetime.date(int(apunte.date_maturity[:4]), int(apunte.date_maturity[5:7]), dia_vencimiento)
                                fecha_anterior = apunte.date_maturity
                                ffa = True
                    _logger.info(factura.move_id)
                    # Publicamos el asiento
                    factura.move_id.post()
                #if factura.move_id and not fecha_vencimiento:

            _logger.info('--->>>>>>>>> DATOS QUE FALTAN')
            _logger.info(company.name)
            _logger.info(modo_de_pago_falta)
            _logger.info(mandato_cliente_falta)
            _logger.info("Casos a normalizar")
            _logger.info(casosanormalizar)
