from odoo import models, fields


class OpBatchSubjectRel(models.Model):
    _name = 'op.batch.subject.rel'

    batch_id = fields.Many2one('op.batch')
    subject_id = fields.Many2one('op.subject')

    hours = fields.Float(string="Hours")
    credits = fields.Float(string="Credits")
    ects = fields.Integer(string="ECTS", default=0)
    nif_faculty = fields.Char(string="Teacher's nif", size=20)
    evaluable = fields.Boolean(string='Is evaluable', default=True)
    level = fields.Char(string="Level", size=1)
    optional = fields.Boolean(string='Is optional', default=False)
    order = fields.Integer(string='Order')

    _sql_constrains = [
        ('unique_batch_id_subject_id_', 'unique( batch_id, subject_id)', 'The Batch Id & Subject Id must be UNIQUE')
    ]
