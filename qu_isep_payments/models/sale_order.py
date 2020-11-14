# -*- coding: utf-8 -*-
# © 2018 Qubiq 2010
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError
#from gmri import *
import logging
import datetime

_logger = logging.getLogger(__name__)


def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '%.12f' % f
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])


class sale_order(models.Model):
    _inherit = 'sale.order'

    curso = fields.Boolean(string="Curso", default=True)
    diario_id = fields.Many2one('account.journal', string="Diario", compute="_get_diario", readonly=True)
    precio_matricula = fields.Float(compute='_get_precio_matricula', string='Precio matrícula', digits=(12, 2))
    precio_entrega = fields.Float(compute='_get_precio_gastos_entrega', string='Precio entrega', digits=(12, 2))
    precio_primer_pago = fields.Float(compute='_get_primer_pago_mensual', string='Precio primer pago', digits=(12, 2))
    precio_ultimo_pago = fields.Float(compute='_get_ultimo_pago_mensual', string='Precio último pago', digits=(12, 2))
    precio_total_curso = fields.Float(compute='_get_total_cursos', string='Precio total curso', digits=(12, 2))
    len_cuotas = fields.Integer(compute="_get_cuotas", string="Quotas")
    fecha_primer_pago = fields.Date(compute="_get_fecha_primer_pago", string="Fecha primer pago")
    cuenta_bancaria = fields.Many2one('res.partner.bank', string="Cuenta bancaria")
    tarjeta_credito = fields.Many2one('payment.method', string="Tarjeta de crédito")
    payment_mode_id_name = fields.Char(string="nombre modo de pago", related="payment_mode_id.name")
    mandate_id = fields.Many2one('account.banking.mandate', string="Mandato")
    x_enviado_crm = fields.Boolean(string="Enviado al CRM", default=False, copy=False)
    
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

    """
    Función para la generación de pagos en la tabla de isep pagos.
    Notas:
        * Todos los productos sin el campo 'tipodecurso' definido los discrimina.
        * Las lineas del plazo de pago que no sea percent o balance las discrimina.
    """
    """
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
    Se realiza una herencia para que en el momento de guardar gestione
    el producto de financiacion.
 
    @api.multi
    def write(self, values):
        result = super(sale_order, self).write(values)
        for sel in self:
            sel._change_payment_term_id()
        return result

 
    Se realiza una herencia para que en el momento de crear gestione
    el producto de financiacion.

    @api.model
    def create(self, vals):
        result = super(sale_order, self).create(vals)
        for sel in result:
            sel._change_payment_term_id()
        return result


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
        for order in self:
            if order.curso and len(order.invoice_ids) == 1:
                if order.diario_id:
                    order.invoice_ids.journal_id = order.diario_id
                    order.invoice_ids.payment_mode_id = order.payment_mode_id
                else:
                    raise ValidationError(_("Hay un error con el diario en ventas."))

    @api.multi
    def action_confirm(self):
        for sel in self:
            sel.partner_id.customer = True
            sel.partner_invoice_id.customer = True
            text_error = ''
            if not sel.x_Matricula_Pagada:
                text_error += "No se ha pagado la matrícula.\n"
            # if sel.payment_mode_id_name == 'Datáfono' and not sel.tarjeta_credito:
            #     text_error += "No se ha seleccionado una tarjeta de crédito.\n"
            if sel.payment_mode_id_name == 'Domiciliado' and not sel.cuenta_bancaria:
                text_error += "No se ha seleccionado una cuenta bancaria.\n"
            if sel.payment_mode_id_name == 'Domiciliado' and not sel.mandate_id:
                text_error += "No se ha seleccionado un mandato bancario.\n"
            if not sel.payment_mode_id:
                text_error += "No se ha seleccionado un modo de pago.\n"
            if not self.partner_id.country_id:
                text_error += "No se ha seleccionado un país para este cliente.\n"
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
        tarjeta_obj = self.env['payment.method'].create(vals_tarjeta)
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
                        'signature_date': datetime.date.today().replace(day=01).replace(month=9),
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
                    if not self.env['payment.method'].search([
                        ('partner_id', '=', sale_order.partner_invoice_id.id),
                        ('acquirer_ref', '=', sale_order.x_Tarjeta.replace(' ', ''))
                            ]):
                        sale_order._crear_tarjeta_credito(company.id)
                        _logger.info("<<-- CREO TARJETA")
