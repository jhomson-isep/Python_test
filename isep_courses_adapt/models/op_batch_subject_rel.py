# -*- coding: utf-8 -*-

from odoo import models, fields
from .op_sql import SQL
import logging
import os

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
        ('unique_batch_id_subject_id_', 'unique( batch_id, subject_id)', 'The Batch Id & Subject Id must be UNIQUE')
    ]

    def import_subjects_rel(self):
        s = SQL()
        logger.info("**************************************")
        logger.info("import subjects rel")
        logger.info("**************************************")
        subjects = self.env['op.subject'].search([])
        for subject in subjects:
            try:
                subjects_rel_app = s.get_subject_rel_by_code(subject.code)
                for subject_rel_app in subjects_rel_app:
                    batch = self.env['op.batch'].search([('code', 'ilike', subject_rel_app.Curso_id)], limit=1)
                    existent_subject_rel = self.search([('batch_id', '=', batch.id), ('subject_id', '=', subject.id)])
                    if len(existent_subject_rel) < 1:
                        subject_rel_values = {
                            'batch_id': batch.id,
                            'subject_id': subject.id,
                            'hours': subject_rel_app.Horas,
                            'credits': subject_rel_app.Creditos,
                            'ects': subject_rel_app.ECTS,
                            'nif_faculty': subject_rel_app.NIF_Profesor,
                            'evaluable': subject_rel_app.Evaluable,
                            'level': subject_rel_app.Nivel,
                            'optional': subject_rel_app.Optativa,
                            'order': subject_rel_app.Orden
                        }
                        if batch.id:
                            res = super(OpBatchSubjectRel, self).create(subject_rel_values)
                            print(res)

            except Exception as e:
                logger.info(e)
                continue
