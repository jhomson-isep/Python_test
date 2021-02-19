# -*- encoding: utf-8 -*-
from odoo import fields, models, api

class PracticeScheduleDays(models.Model):
    _name = 'practice.schedule.days'
    _description = "Schedule of days"
    _rec_name = 'day'

    day = fields.Selection([
        ('monday', 'Lunes'),
        ('tuesday', 'Martes'),
        ('wednesday', 'Miercoles'),
        ('thursday', 'Jueves'),
        ('friday', 'Viernes'),
        ('saturday', 'Sabado'),
    ], 'Day')
    practice_schedule_id = fields.Many2one('practice.schedule', string="Schedule", required=True)

    def getDay(self):
        return dict(self._fields['day'].selection).get(self.day)



