from odoo import models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"
    category_id = fields.Many2one('product.category',
                                  string='Categoria Producto:',
                                  compute='_set_category')


def _set_category(self):
    self.category_id = self.x_curso_id.category_id.id
