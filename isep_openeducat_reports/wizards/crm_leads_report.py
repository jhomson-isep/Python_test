# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CrmLeaReportWizard(models.TransientModel):
    _name = 'crm.lead.report'
    date_init = fields.Date("Initial Date:")
    date_end = fields.Date("End Date:")

    def print_crm_lead_report(self):
        if self.date_init > self.date_end:
            raise ValidationError(
                _("La fecha inicial no puede ser mayor a la fecha final!!!"))
        data = {
            'model': 'crm.lead.report',
            'form': self.read()[0],
        }
        logger.info(data)
        cmr_leads = self.env['crm.lead'].search(
            [('date_open', '>=', fields.Date.to_string(self.date_init)),
             ('date_open', '<=', fields.Date.to_string(self.date_end))])
        leads = []
        for lead in cmr_leads:
            type_lead = {
                'lead': 'iniciativa',
                'opportunity': 'oportunidad'
            }
            archive = {
                True: 'Si',
                False: 'No',
            }
            street = lead.street if lead.street else ''
            street = street + lead.street2 if lead.street2 else ''
            vals = {
                'id': lead.id,
                'Fecha': lead.date_open,
                'Estado': lead.stage_id.name or '',
                'Contacto': lead.partner_id.name or '',
                'Direccion': street,
                'Correo Electronico': lead.email_from or '',
                'Telefono': lead.phone or '',
                'Codigo postal': lead.zip or '',
                'Compañia': lead.company_id.name or '',
                'País': lead.country_id.name or '',
                'Ciudad': lead.city or '',
                'Tipo': type_lead[lead.type],
                'Archivado': archive[lead.active]
            }
            leads.append(vals)
        data['leads'] = leads
        report = self.env.ref('isep_openeducat_reports.report_crm_leads')
        return report.report_action(self, data=data)
