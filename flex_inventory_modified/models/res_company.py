from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'


    show_inventory_modified = fields.Boolean(string='Show Inventory Modified', default=False)