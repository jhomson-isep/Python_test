from odoo import models

class CrmLeadXlsx(models.AbstractModel):
    _name = 'report.isep_openeducat_reports.report_crm_leads'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, students):
        pass