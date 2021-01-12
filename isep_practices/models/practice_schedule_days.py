from odoo import fields, models

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
    ], 'Day')
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    practice_schedule_id = fields.Many2one('practice.schedule', string="Schedule", required=True)
