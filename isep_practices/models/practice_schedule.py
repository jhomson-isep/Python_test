from odoo import fields, models

class PracticeSchedule(models.Model):
    _name = 'practice.schedule'
    _description = "Schedule"

    name = fields.Char(string='Name', size=200)
    practice_schedule_days_ids = fields.One2many('practice.schedule.days', 'practice_schedule_id')