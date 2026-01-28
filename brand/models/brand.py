from odoo import fields, models, api, _


class Brand(models.Model):
    _name = 'brand'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True)


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('brand', string='Brand')

