from odoo import fields, api, models
import logging

logger = logging.getLogger(__name__)


class OpStudent(models.Model):
    _name = 'op.student'
    _inherit = ['op.student', 'mail.thread']

    partner_id = fields.Many2one('res.partner', string='Partner')
    campus_id = fields.Many2one('op.campus', string='Campus')
    uvic_documentation = fields.Boolean(string='UVIC Documentation', default=False)
    rvoe_documentation = fields.Boolean(string='RVOE Documentation', default=False)
    curp = fields.Char(string='CURP', size=20)
    yer_end_studies = fields.Integer(string='Year of completion of studies')
    document_type_id = fields.Many2one('op.document.type', string='Document type')
    document_number = fields.Char(string='Document number', size=32)
    contact_type_id = fields.Many2one('op.contact.type', string='Contact type')
    study_type_id = fields.Many2one('op.study.type', string='Study type')

    moodle_id = fields.Integer(string='Moodle ID')
    moodle_pass = fields.Char(string='Moodle Password', size=24)
