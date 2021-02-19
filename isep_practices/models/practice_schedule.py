# -*- encoding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class PracticeSchedule(models.Model):
    _name = 'practice.schedule'
    _description = "Schedule"

    name = fields.Char(string='Name', compute="_compute_day", store=True)
    turn = fields.Selection([
        ('morning', 'Mañana'),
        ('afternoon', 'Tarde'),
        ('both', 'Mañana/Tarde'),
    ], 'Turn')
    practice_schedule_days_ids = fields.One2many('practice.schedule.days', 'practice_schedule_id')

    def getTurn(self):
        return dict(self._fields['turn'].selection).get(self.turn)

    @api.one
    @api.depends('practice_schedule_days_ids.day', 'turn')
    def _compute_day(self):
        self.name = ', '.join(days.getDay() for days in self.practice_schedule_days_ids)
        if self.name and self.turn:
            self.name = self.name + ' - ' + str(self.getTurn())

    @api.onchange('practice_schedule_days_ids')
    def _validation_schedule_day(self):
        validate_day = {'monday': 0, 'tuesday': 0, 'wednesday': 0, 'thursday': 0, 'friday': 0, 'saturday': 0}
        for days in self.practice_schedule_days_ids:
            if days.day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:
                validate_day[days.day] += 1
            if validate_day[days.day] > 1:
                raise ValidationError(
                    _("Day exist"))

    _sql_constraints = [
        ('unique_name',
         'unique(name)',
         'Day must be unique per schedule!'),
    ]

