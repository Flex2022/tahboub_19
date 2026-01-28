from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_purchase_admin = fields.Boolean(string='Is Purchase Admin',compute='_compute_is_purchase_admin')

    @api.depends()
    def _compute_is_purchase_admin(self):
        if self.env.user.has_group('purchase.group_purchase_manager'):
            self.is_purchase_admin = True
        else:
            self.is_purchase_admin = False

