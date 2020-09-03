from odoo import models, fields, api, _
import logging

class CrmLead(models.model):
    _inherit = 'crm.lead'

    zapier = fields.Checkbox('crm.lead', string="¿Proviene de Zapier?")