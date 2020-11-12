from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'
    partner_assigned = fields.Many2one('res.partner',
                                       string="Responsable de tarea")
    ticket_type = fields.Selection([
        ('feature', 'Funcionalidad'),
        ('fix', 'Error')
    ], string='Tipo de tarea', required=True, default='feature')
