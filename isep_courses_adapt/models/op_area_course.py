from odoo import models, fields


class OpAreaCourse(models.Model):
    _name = 'op.area.course'

    name = fields.Char(string="Name of Area")
    code = fields.Char(string="Code of Area")

    _sql_constraints = [('unique_area_code',
                         'unique(code)', 'Code should be unique per area!')]