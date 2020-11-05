# -*- coding: utf-8 -*-

from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    require_signature = fields.Boolean('Online Signature',
                                       default=True,
                                       readonly=True,
                                       states={'draft': [('readonly', False)],
                                               'sent': [('readonly', False)]},
                                       help='Request a online signature to the customer in order to confirm orders automatically.')
    signature = fields.Binary('Signature',
                              help='Signature received through the portal.',
                              copy=False, attachment=True)
    signed_by = fields.Char('Signed by',
                            help='Name of the person that signed the SO.',
                            copy=False)
