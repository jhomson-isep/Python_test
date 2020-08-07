# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError
import base64
import csv
from io import *
import logging
from datetime import date
_logger = logging.getLogger(__name__)


# diario -> Importacion academico, por compañia
class ImportCobrosAcademica(models.TransientModel):
    _name = 'import.cobros.academica'
    data = fields.Binary('Archivo', required=True)
    name = fields.Char('Nombre del archivo')
    delimeter = fields.Char('Delimitador', default=',')
    company_id = fields.Many2one(
        'res.company',
        string='Compañia',
        default=lambda self: self.env.user.company_id,
        readonly=True
    )

    def _comprobacion_cabecera(self, keys):
        _logger.info(keys)
        state = True
        if 'tipo' not in keys:
            state = False
        if 'codformapago' not in keys:
            state = False
        if 'fecha' not in keys:
            state = False
        if 'nofactura' not in keys:
            state = False
        if 'alumno' not in keys:
            state = False
        if 'niftitular' not in keys:
            state = False
        if 'importe' not in keys:
            state = False
        return state

    def _crear_asiento(self, diario_id):
        vals = {
            'journal_id': diario_id,
            'company_id': self.company_id.id,
            'date': fields.Date.context_today(self),
            'ref': 'Migración académica, ' + str(fields.Datetime.now())
        }
        return self.env['account.move'].create(vals)

    def _crear_apuntes(self, values, asiento, cuentas):
        fecha = date(
            year=int(values['fecha'][:10].split('/')[2]),
            month=int(values['fecha'][:10].split('/')[1]),
            day=int(values['fecha'][:10].split('/')[0]))
        vals = {
            'name': values['nofactura']+', '+values['alumno']+', '+values['niftitular'],
            'journal_id': asiento.journal_id.id,
            'move_id': asiento.id,
            'company_id': self.company_id.id,
            'account_id': cuentas[values['codformapago']]['debe'],
            'debit': float(values['importe'].replace(',', '.')) or 0.0,
            'credit': 0.0,
            'date': fecha,
            'date_maturity': fecha,
        }
        partner = False
        if values['niftitular'] != '':
            partner_aux = self.env['res.partner'].search([
                ('company_id', '=', self.company_id.id),
                ('vat', 'like', values['niftitular'])
                ])
            if len(partner_aux) == 1:
                partner = partner_aux.id
        if not partner and values['alumno']:
            partner_aux = self.env['res.partner'].search([
                ('company_id', '=', self.company_id.id),
                ('name', 'like', values['alumno'])
                ])
            if len(partner_aux) == 1:
                partner = partner_aux.id
        vals['partner_id'] = partner
        self.env['account.move.line'].create(vals)
        vals['account_id'] = cuentas[values['codformapago']]['haber']
        vals['credit'] = float(values['importe'].replace(',', '.')) or 0.0
        vals['debit'] = 0.0
        self.env['account.move.line'].create(vals)

    def _search_cuentas(self):
        res = {}
        cuentas_clas = self.env['account.account']
        res['DO'] = {
            'debe': cuentas_clas.search([
                ('code', '=', '431000'),
                ('company_id', '=', self.company_id.id)
                ], limit=1).id,
            'haber': cuentas_clas.search([
                ('code', '=', '430000'),
                ('company_id', '=', self.company_id.id)
                ], limit=1).id}
        res['DT'] = {
            'debe': cuentas_clas.search([
                ('code', '=', '555013'),
                ('company_id', '=', self.company_id.id)
                ], limit=1).id,
            'haber': res['DO']['haber']}
        res['EF'] = {
            'debe': cuentas_clas.search([
                ('code', '=', '555011'),
                ('company_id', '=', self.company_id.id)
                ], limit=1).id,
            'haber': res['DO']['haber']}
        res['TR'] = {
            'debe': cuentas_clas.search([
                ('code', '=', '555012'),
                ('company_id', '=', self.company_id.id)
                ], limit=1).id,
            'haber': res['DO']['haber']}
        res[''] = {
            'debe': res['DO']['haber'],
            'haber': cuentas_clas.search([
                ('code', '=', '431002'),
                ('company_id', '=', self.company_id.id)
                ], limit=1).id}
        return res

    @api.multi
    def action_import(self):
        if not self.data:
            raise ValidationError("Se tiene que seleccionar una archivo!")
        # Decode the file data
        data = base64.b64decode(self.data)
        file_input = cStringIO.StringIO(data)
        file_input.seek(0)
        reader_info = []
        if self.delimeter:
            delimeter = str(self.delimeter)
        else:
            delimeter = ','
        reader = csv.reader(file_input, delimiter=delimeter,
                            lineterminator='\r\n')
        try:
            reader_info.extend(reader)
        except Exception:
            raise ValidationError("El fichero no es valido!")
        keys = reader_info[0]
        # Update column names
        keys_init = reader_info[0]
        keys = []
        for k in keys_init:
            temp = k.replace(' ', '_')
            keys.append(temp.lower())
        if self._comprobacion_cabecera(keys):
            del reader_info[0]
            values = {}
            # Import data to temporary table
            diario_id = self.env['account.journal'].search([
                ('name', 'like', 'Importación académico %'),
                ('company_id', '=', self.company_id.id)
                ], limit=1).id or False
            if not diario_id:
                raise ValidationError("No se encuentra el diario de importacion.")
            asiento = self._crear_asiento(diario_id)
            if not asiento:
                raise ValidationError("No se ha creado bien el asiento!")
            cuentas = self._search_cuentas()
            if not cuentas:
                raise ValidationError("No se han podido encontrar las cuentas.")
            for i in range(len(reader_info)):
                try:
                    field = reader_info[i]
                    values = dict(zip(keys, field))
                    _logger.info(values)
                    if values['alumno'] != '' and values['niftitular'] != '':
                        if values['fecha'] != '':
                            self._crear_apuntes(values, asiento, cuentas)
                        else:
                            raise ValidationError("La linea "+str(i+1)+", no tiene fecha!")
                    else:
                        raise ValidationError("La linea "+str(i+1)+", no tiene nombre ni dni!")
                except Exception:
                    raise ValidationError("Error en la linea: " + str(i+1)
                                               + '.')
        else:
            raise ValidationError("Las cabeceras no son correctas! \n Son: \n" + str(keys)
                + '\n Deben ser: \n tipo, codformapago, fecha, nofactura, alumno, niftitular, importe')
        return {'type': 'ir.actions.act_window_close'}
