# -*- coding: utf-8 -*-

from odoo import models, fields, api
from .op_sql import SQL
import logging

logger = logging.getLogger(__name__)


class OpBatchSubjectRel(models.Model):
    _name = 'op.batch.subject.rel'
    _description = "Subject relations"

    batch_id = fields.Many2one('op.batch', string="Batch")
    subject_id = fields.Many2one('op.subject', string="Subject")
    hours = fields.Float(string="Hours")
    credits = fields.Float(string="Credits")
    ects = fields.Integer(string="ECTS", default=0)
    nif_faculty = fields.Char(string="Teacher's NIF", size=20)
    evaluable = fields.Boolean(string='Is evaluable', default=True)
    level = fields.Char(string="Level", size=1)
    optional = fields.Boolean(string='Is optional', default=False)
    order = fields.Integer(string='Order')

    _sql_constrains = [
        ('unique_batch_id_subject_id_', 'unique( batch_id, subject_id)',
         'The Batch Id & Subject Id must be UNIQUE')
    ]

    def import_all_subjects_rel(self):
        s = SQL()
        logger.info("**************************************")
        logger.info("import subjects rel")
        logger.info("**************************************")
        subjects_rel = s.get_all_subject_rel()
        for subject_rel in subjects_rel:
            try:
                batch = self.env['op.batch'].search(
                    [('code', '=', subject_rel.Curso_id)], limit=1)
                subject = self.env['op.subject'].search(
                    [('code', '=', subject_rel.CodAsignatura)])
                existent_subject_rel = self.search(
                    [('batch_id', '=', batch.id),
                     ('subject_id', '=', subject.id)])
                if len(existent_subject_rel) < 1:
                    subject_rel_values = {
                        'batch_id': batch.id,
                        'subject_id': subject.id,
                        'hours': subject_rel.Horas,
                        'credits': subject_rel.Creditos,
                        'ects': subject_rel.ECTS,
                        'nif_faculty': subject_rel.NIF_Profesor,
                        'evaluable': subject_rel.Evaluable,
                        'level': subject_rel.Nivel,
                        'optional': subject_rel.Optativa,
                        'order': subject_rel.Orden
                    }
                    if batch.id:
                        res = super(OpBatchSubjectRel, self).create(
                            subject_rel_values)
                        print(res)

            except Exception as e:
                logger.info(e)
                continue
