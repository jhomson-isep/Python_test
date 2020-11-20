# -*- coding: utf-8 -*-
# © 2018 Qubiq 2010
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import api, fields, models, _
from openerp.exceptions import UserError
import datetime
_logger = logging.getLogger(__name__)


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    sale_order_ids = fields.Many2many('sale.order', compute='compute_sale_orders')
    prorata_financiacion_lineas = fields.Integer(string="prorrata de la financiacion", compute="_get_prorata_financiacion_lineas")
    mail_to_factura_validada = fields.Char(string="Cuenta de Mail para el mail atomatico", compute="_get_mail_to_factura_validada")
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
        for sel in self:
            if 'isep' in sel.company_id.name.lower():
                sel.mail_to_factura_validada = "ollorente@grupoisep.com"
            else:
                sel.mail_to_factura_validada = "nmolina@grupoisep.com"

    @api.multi
    def _get_name_to_factura_validada(self):
        for sel in self:
            if 'isep' in sel.company_id.name.lower():
                sel.name_to_factura_validada = "Oscar"
            else:
                sel.name_to_factura_validada = "Noemí"
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
                    if line_obj.account_id.code == '430000':
                        if bool_matricula:
                            line_matricula = line_obj.copy()
                            line_matricula.name = pagos_objs[pagos_recorridos].name
                            line_matricula.date_maturity = datetime.datetime.strptime(pagos_objs[pagos_recorridos].fecha.split(" ")[0], '%Y-%m-%d')
                            line_matricula.debit = pagos_objs[pagos_recorridos].importe
                            bool_matricula = False
                            pagos_recorridos += 1
                        if bool_gasto_envio:
                            line_matricula = line_obj.copy()
                            line_matricula.name = pagos_objs[pagos_recorridos].name
                            line_matricula.date_maturity = datetime.datetime.strptime(pagos_objs[pagos_recorridos].fecha.split(" ")[0], '%Y-%m-%d')
                            line_matricula.debit = pagos_objs[pagos_recorridos].importe
                            bool_gasto_envio = False
                            pagos_recorridos += 1
                        line_obj.name = pagos_objs[pagos_recorridos].name
                        line_obj.date_maturity = datetime.datetime.strptime(pagos_objs[pagos_recorridos].fecha.split(" ")[0], '%Y-%m-%d')
                        line_obj.debit = pagos_objs[pagos_recorridos].importe
                        pagos_recorridos += 1
            # Publicamos el asiento
            self.move_id.post()
        else:
            raise UserError(_('No se ha creado el Asiento.'))
        # raise UserError(_('Fallo adrede.'))

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
                self.env.ref('isep_custom.email_template_aviso_factura_validada').send_mail(sel.id, force_send=True)
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