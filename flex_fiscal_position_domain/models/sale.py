from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fiscal_position_domain_ids = fields.Many2many(
        comodel_name='account.fiscal.position',
        relation='sale_order_fiscal_position_domain_rel',
        column1='sale_order_id',
        column2='fiscal_position_domain_id',
        string='Fiscal Position Domains',
        compute='_compute_fiscal_position_domain_ids',
    )

    @api.depends('user_id', 'user_id.fiscal_position_domain_ids')
    def _compute_fiscal_position_domain_ids(self):
        for order in self:
            user = order.user_id or self.env.user
            order.fiscal_position_domain_ids = user.fiscal_position_domain_ids

    def sh_import_sol(self):
        """Compatibility hook for legacy SO line import buttons in inherited views."""
        self.ensure_one()
        action = self.env.ref('sh_import_so.sh_action_import_so_wizard', raise_if_not_found=False)
        if action:
            return action._get_action_dict()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Import Sale Order Lines',
                'message': 'Legacy SO line import feature is not installed in this environment.',
                'type': 'warning',
                'sticky': False,
            },
        }
