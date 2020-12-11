# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

logger = logging.getLogger(__name__)


class BatchStudents(models.TransientModel):
    _name = 'batch.students'

    def print_batch_students_report(self):
        data = {
            'model': 'op.batch',
            'form': self.read()[0]
        }

        return self.env.ref('isep_openeducat_reports.report_batch_students').report_action(self, data=data)
