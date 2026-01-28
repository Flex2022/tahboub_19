# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


# from odoo.exceptions import UserError, ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_tax_readonly_sale = fields.Boolean(string='Readonly Tax')
    is_separate_sol = fields.Boolean("Separate order lines based on category")
    wood_categs = fields.Many2many('product.category', relation='wood_categs_company_rel', string='Wood Categories')
    accessory_categs = fields.Many2many('product.category', relation='accessory_categs_company_rel',
                                        string='Accessories')
    mixer_categs = fields.Many2many('product.category', relation='mixer_categs_company_rel', string='Sinks & Mixers')
    electronic_categs = fields.Many2many('product.category', relation='electronic_categs_company_rel',
                                         string='Electronics')
    worktop_categs = fields.Many2many('product.category', relation='worktop_categs_company_rel', string='Worktops')
    service_categs = fields.Many2many('product.category', relation='service_categs_company_rel', string='Services')
    appliance_categs = fields.Many2many('product.category', relation='appliance_categs_company_rel',
                                        string='Appliances')
    bedroom_categs = fields.Many2many('product.category', relation='bedroom_categs_company_rel', string='Bedrooms')

    is_sol_price_editable = fields.Boolean("Editable unit price")
    is_sol_discount_editable = fields.Boolean("Editable Discount")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_separate_sol = fields.Boolean(
        "Separate order lines based on category", related='company_id.is_separate_sol', readonly=False)

    wood_categs = fields.Many2many(
        'product.category', related='company_id.wood_categs', string='Wood', readonly=False)
    accessory_categs = fields.Many2many(
        'product.category', related='company_id.accessory_categs', string='Accessories', readonly=False)
    mixer_categs = fields.Many2many(
        'product.category', related='company_id.mixer_categs', string='Sinks & Mixers', readonly=False)
    electronic_categs = fields.Many2many(
        'product.category', related='company_id.electronic_categs', string='Electromechanical Work', readonly=False)
    worktop_categs = fields.Many2many(
        'product.category', related='company_id.worktop_categs', string='Worktops', readonly=False)
    service_categs = fields.Many2many(
        'product.category', related='company_id.service_categs', string='Services', readonly=False)
    appliance_categs = fields.Many2many(
        'product.category', related='company_id.appliance_categs', string='Electric Hardware', readonly=False)
    bedroom_categs = fields.Many2many(
        'product.category', related='company_id.bedroom_categs', string='Bedrooms', readonly=False)
    selected_categs = fields.Many2many(
        'product.category', compute='_get_selected_categs', string='Selected Categories')

    is_sol_price_editable = fields.Boolean(
        "Editable unit price", related='company_id.is_sol_price_editable', readonly=False)

    is_sol_discount_editable = fields.Boolean(
        "Discount", related='company_id.is_sol_discount_editable', readonly=False)

    @api.depends('is_separate_sol',
                 'wood_categs',
                 'accessory_categs',
                 'mixer_categs',
                 'electronic_categs',
                 'worktop_categs',
                 'service_categs',
                 'appliance_categs',
                 'bedroom_categs',
                 )
    def _get_selected_categs(self):
        for rec in self:
            rec.selected_categs = []
            if rec.is_separate_sol:
                rec.selected_categs = rec.wood_categs + rec.accessory_categs + rec.mixer_categs + rec.electronic_categs + \
                                      rec.worktop_categs + rec.service_categs + rec.appliance_categs + rec.bedroom_categs
