from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    fiscal_position_domain_ids = fields.Many2many(
        comodel_name='account.fiscal.position',
        relation='res_users_fiscal_position_domain_rel',
        column1='user_id',
        column2='fiscal_position_domain_id',
        string='Fiscal Position Domains',
        help='Fiscal positions this user can select on sales orders.',
    )

