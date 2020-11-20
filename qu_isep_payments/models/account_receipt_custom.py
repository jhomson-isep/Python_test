# -*- coding: utf-8 -*-
# © 2018 Qubiq 2010
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import api, fields, models, _
from openerp.report import report_sxw
from openerp.osv import osv
import json
from datetime import datetime
import logging


class AccountReceiptParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(AccountReceiptParser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_details': self.get_details,
            'get_details_inv': self.get_details_inv,
        })
        self.context = context

    def get_details_inv(self, doc):
        lines = []
        acc_inv = self.pool.get('account.invoice').search(self.cr, self.uid, [('id', '=', doc.id)])
        acc_inv_rec = self.pool.get('account.invoice').browse(self.cr, self.uid, acc_inv, context=None)
        total_amount = acc_inv_rec.amount_total
        if acc_inv_rec.state == 'draft':
            balance_amount = total_amount
        else:
            balance_amount = acc_inv_rec.residual
        paid = total_amount - balance_amount
        vals = {
            'total_amount': total_amount,
            'balance_amount': balance_amount,
            'paid': paid,
        }
        lines.append(vals)
        return lines

    def get_details(self, doc):
        lines = []
        acc_inv = self.pool.get('account.invoice').search(
            self.cr, self.uid, [('id', '=', doc.id)])
        acc_inv_rec = self.pool.get('account.invoice').browse(
            self.cr, self.uid, acc_inv, context=None)
        if acc_inv_rec.payments_widget != 'false':
            d = json.loads(acc_inv_rec.payments_widget)
            for payment in d['content']:
                date_object = datetime.strptime(payment['date'], '%Y-%m-%d')
                logging.info("-->>> AQUI")
                logging.info(payment)
                vals = {
                    'memo': '(' in payment['ref'] and payment['ref'].
                            split('(')[-1][:-1] or payment['ref'],
                    'amount': payment['amount'],
                    'method': payment['journal_name'],
                    'date': date_object.strftime('%d-%m-%Y'),
                }
                lines.append(vals)
        return lines


class PrintReport(osv.AbstractModel):
    _name = 'report.payment_receipt_invoice.report_payment'
    _inherit = 'report.abstract_report'
    _template = 'payment_receipt_invoice.report_payment'
    _wrapped_report_class = AccountReceiptParser
