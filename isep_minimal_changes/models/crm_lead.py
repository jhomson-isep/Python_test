from odoo import models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"
    category_id = fields.Many2one('product.category',
                                  string='Categoria Producto:',
                                  related='product_id.category_id')
