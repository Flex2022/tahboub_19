from odoo import models, api, fields, _
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = 'res.company'

    use_price_map = fields.Boolean(string='Enable Price Mapping In Sale?')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_price_map = fields.Boolean(
        string='Enable Price Mapping In Sale?', related='company_id.use_price_map', readonly=False)

