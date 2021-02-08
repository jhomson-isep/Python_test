from odoo import models


class CrmLeadXlsx(models.AbstractModel):
    _name = 'report.isep_openeducat_reports.report_crm_leads'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, crm_lead_report):
        sheet = workbook.add_worksheet('Reporte Iniciativas/Oportunidades')
        bold = workbook.add_format({'bold': True})
        # 'Columns'
        for item in data['leads']:
            for i, key in enumerate(item.keys()):
                sheet.write(0, i, key, bold)
            break
        # 'Rows'
        for i, item in enumerate(data['leads'], start=1):
            for j, key in enumerate(item.keys()):
                sheet.write(i, j, item[key])
