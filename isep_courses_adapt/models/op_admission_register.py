# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
import logging

from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class OpAdmissionRegister(models.Model):
    _inherit = 'op.admission.register'

    batch_id = fields.Many2one('op.batch', string='Batch', required=True)
    product_id = fields.Many2one(
        'product.product', 'Course Fees', required=False,
        domain=[('type', '=', 'service')], readonly=True,
        states={'draft': [('readonly', False)]}, track_visibility='onchange')

    # @api.one
    # @api.onchange('batch_id')
    # def change_name(self):
    #     if self.batch_id.name:
    #         self.name = self.batch_id.name

    def generate_admissions_register(self):
        batches = self.env['op.batch'].search([])
        for batch in batches:
            try:
                ar_count = self.search_count(
                    [('batch_id.code', '=', batch.code)])
                if ar_count == 0:
                    admission_values = {
                        'batch_id': batch.id,
                        'name': batch.code,
                        'course_id': batch.course_id.id,
                        'start_date': batch.start_date,
                        'end_date': batch.end_date,
                        'max_count': batch.students_limit,
                    }
                    logger.info(admission_values)
                    res = super(OpAdmissionRegister, self).create(
                        admission_values)
                    res.start_admission()
                else:
                    logger.info("Already exist: {}".format(batch.code))
            except Exception as e:
                logger.info(e)
                continue

    # Delete after implementation
    @api.multi
    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        for record in self:
            start_date = fields.Date.from_string(record.start_date)
            end_date = fields.Date.from_string(record.end_date)
            if start_date > end_date:
                logger.info("End Date cannot be set before Start Date.")
                # raise ValidationError(
                #     _("End Date cannot be set before Start Date."))
