# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from lxml import etree
from odoo.exceptions import UserError, ValidationError

from odoo.tools import is_html_empty

states_readonly = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_invoice_id = fields.Many2one('res.partner', domain="[('id', 'child_of', partner_id)]")
    # partner_shipping_id = fields.Many2one('res.partner', domain="[('id', 'child_of', partner_id)]")
    warehouse_id = fields.Many2one('stock.warehouse', default=False)
    commitment_date = fields.Datetime(copy=True)

    customer_project_id = fields.Many2one('customer.project', string='Project Name', states=states_readonly)

    is_separate_sol = fields.Boolean(
        "Separate order lines based on category", related='company_id.is_separate_sol')

    wood_categs = fields.Many2many(
        'product.category', related='company_id.wood_categs')
    accessory_categs = fields.Many2many(
        'product.category', related='company_id.accessory_categs')
    mixer_categs = fields.Many2many(
        'product.category', related='company_id.mixer_categs')
    electronic_categs = fields.Many2many(
        'product.category', related='company_id.electronic_categs')
    worktop_categs = fields.Many2many(
        'product.category', related='company_id.worktop_categs')
    service_categs = fields.Many2many(
        'product.category', related='company_id.service_categs')
    appliance_categs = fields.Many2many(
        'product.category', related='company_id.appliance_categs')
    bedroom_categs = fields.Many2many(
        'product.category', related='company_id.bedroom_categs')

    wood_order_line = fields.One2many(
        'sale.order.line', 'order_id', domain=[('categ_type', '=', 'wood')], states=states_readonly, )
    accessory_order_line = fields.One2many(
        'sale.order.line', 'order_id', domain=[('categ_type', '=', 'accessory')], states=states_readonly, )
    mixer_order_line = fields.One2many(
        'sale.order.line', 'order_id', domain=[('categ_type', '=', 'mixer')], states=states_readonly, )
    electronic_order_line = fields.One2many(
        'sale.order.line', 'order_id', domain=[('categ_type', '=', 'electronic')], states=states_readonly, )
    worktop_order_line = fields.One2many(
        'sale.order.line', 'order_id', domain=[('categ_type', '=', 'worktop')], states=states_readonly, )
    service_order_line = fields.One2many(
        'sale.order.line', 'order_id', domain=[('categ_type', '=', 'service')], states=states_readonly, )
    appliance_order_line = fields.One2many(
        'sale.order.line', 'order_id', domain=[('categ_type', '=', 'appliance')], states=states_readonly, )
    bedroom_order_line = fields.One2many(
        'sale.order.line', 'order_id', domain=[('categ_type', '=', 'bedroom')], states=states_readonly, )

    wood_unit_prices = fields.Float(string='Unit Prices', compute='_compute_wood_totals')

    wood_untaxed = fields.Float(string='Untaxed Amount', compute='_compute_wood_totals')
    wood_tax = fields.Float(string='Tax Amount', compute='_compute_wood_totals')
    wood_total = fields.Float(string='Total Amount', compute='_compute_wood_totals')
    wood_undiscounted = fields.Float(string='Amount Before Discount', compute='_compute_wood_undiscounted')
    wood_discount_amount = fields.Float(string='Discount Amount', compute='_compute_wood_discount_amount')


    accessory_untaxed = fields.Float(string='Untaxed Amount', compute='_compute_accessory_totals')
    accessory_tax = fields.Float(string='Tax Amount', compute='_compute_accessory_totals')
    accessory_total = fields.Float(string='Total Amount', compute='_compute_accessory_totals')
    accessory_unit_prices = fields.Float(string='Unit Prices', compute='_compute_accessory_totals')
    accessory_undiscounted = fields.Float(string='Amount Before Discount', compute='_compute_accessory_undiscounted')
    accessory_discount_amount = fields.Float(string='Discount Amount', compute='_compute_accessory_discount_amount')

    mixer_untaxed = fields.Float(string='Untaxed Amount', compute='_compute_mixer_totals')
    mixer_tax = fields.Float(string='Tax Amount', compute='_compute_mixer_totals')
    mixer_total = fields.Float(string='Total Amount', compute='_compute_mixer_totals')
    mixer_unit_prices = fields.Float(string='Unit Prices', compute='_compute_mixer_totals')
    mixer_undiscounted = fields.Float(string='Amount Before Discount', compute='_compute_mixer_undiscounted')
    mixer_discount_amount = fields.Float(string='Discount Amount', compute='_compute_mixer_discount_amount')

    electronic_untaxed = fields.Float(string='Untaxed Amount', compute='_compute_electronic_totals')
    electronic_tax = fields.Float(string='Tax Amount', compute='_compute_electronic_totals')
    electronic_total = fields.Float(string='Total Amount', compute='_compute_electronic_totals')
    electronic_unit_prices = fields.Float(string='Unit Prices', compute='_compute_electronic_totals')
    electronic_undiscounted = fields.Float(string='Amount Before Discount', compute='_compute_electronic_undiscounted')
    electronic_discount_amount = fields.Float(string='Discount Amount', compute='_compute_electronic_discount_amount')

    worktop_untaxed = fields.Float(string='Untaxed Amount', compute='_compute_worktop_totals')
    worktop_tax = fields.Float(string='Tax Amount', compute='_compute_worktop_totals')
    worktop_total = fields.Float(string='Total Amount', compute='_compute_worktop_totals')
    worktop_unit_prices = fields.Float(string='Unit Prices', compute='_compute_worktop_totals')
    worktop_undiscounted = fields.Float(string='Amount Before Discount', compute='_compute_worktop_undiscounted')
    worktop_discount_amount = fields.Float(string='Discount Amount', compute='_compute_worktop_discount_amount')

    service_untaxed = fields.Float(string='Untaxed Amount', compute='_compute_service_totals')
    service_tax = fields.Float(string='Tax Amount', compute='_compute_service_totals')
    service_total = fields.Float(string='Total Amount', compute='_compute_service_totals')
    service_unit_prices = fields.Float(string='Unit Prices', compute='_compute_service_totals')
    service_undiscounted = fields.Float(string='Amount Before Discount', compute='_compute_service_undiscounted')
    service_discount_amount = fields.Float(string='Discount Amount', compute='_compute_service_discount_amount')

    appliance_untaxed = fields.Float(string='Untaxed Amount', compute='_compute_appliance_totals')
    appliance_tax = fields.Float(string='Tax Amount', compute='_compute_appliance_totals')
    appliance_total = fields.Float(string='Total Amount', compute='_compute_appliance_totals')
    appliance_unit_prices = fields.Float(string='Unit Prices', compute='_compute_appliance_totals')
    appliance_undiscounted = fields.Float(string='Amount Before Discount', compute='_compute_appliance_undiscounted')
    appliance_discount_amount = fields.Float(string='Discount Amount', compute='_compute_appliance_discount_amount')

    bedroom_untaxed = fields.Float(string='Untaxed Amount', compute='_compute_bedroom_totals')
    bedroom_tax = fields.Float(string='Tax Amount', compute='_compute_bedroom_totals')
    bedroom_total = fields.Float(string='Total Amount', compute='_compute_bedroom_totals')
    bedroom_unit_prices = fields.Float(string='Unit Prices', compute='_compute_bedroom_totals')
    bedroom_undiscounted = fields.Float(string='Amount Before Discount', compute='_compute_bedroom_undiscounted')
    bedroom_discount_amount = fields.Float(string='Discount Amount', compute='_compute_bedroom_discount_amount')

    wood_untaxed_egp = fields.Float('Wood Untaxed Amount (EGP)', compute='compute_wood_untaxed_egp')
    wood_tax_egp = fields.Float('Wood Tax Amount (EGP)', compute='compute_wood_untaxed_egp')
    wood_total_egp = fields.Float('Wood Total Amount (EGP)', compute='compute_wood_untaxed_egp')
    wood_unit_prices_egp = fields.Float('Wood Unit Prices (EGP)', compute='compute_wood_untaxed_egp')
    wood_undiscounted_egp = fields.Float('Amount Before Discount Eg', compute='_compute_wood_undiscounted_eg', digits=0)
    wood_discount_amount_egp = fields.Float('Discount Amount Eg', compute='_compute_wood_discount_amount_egp')

    @api.depends('wood_undiscounted')
    def _compute_wood_undiscounted_eg(self):
        for order in self:
            order.wood_undiscounted_egp = order.wood_undiscounted * order.additional_currency_rate


    @api.depends('wood_discount_amount','additional_currency_rate')
    def _compute_wood_discount_amount_egp(self):
        for order in self:
            order.wood_discount_amount_egp = order.wood_discount_amount * order.additional_currency_rate



    bedroom_untaxed_egp = fields.Float('Bedroom Untaxed Amount (EGP)', compute='compute_bedroom_untaxed_egp')
    bedroom_tax_egp = fields.Float('Bedroom Tax Amount (EGP)', compute='compute_bedroom_untaxed_egp')
    bedroom_total_egp = fields.Float('Bedroom Total Amount (EGP)', compute='compute_bedroom_untaxed_egp')
    bedroom_unit_prices_egp = fields.Float('Bedroom Unit Prices (EGP)', compute='compute_bedroom_untaxed_egp')
    bedroom_undiscounted_egp = fields.Float('Amount Before Discount Eg', compute='_compute_bedroom_undiscounted_eg', digits=0)
    bedroom_discount_amount_egp = fields.Float('Discount Amount Eg', compute='_compute_bedroom_discount_amount_egp')

    @api.depends('bedroom_undiscounted')
    def _compute_bedroom_undiscounted_eg(self):
        for order in self:
            order.bedroom_undiscounted_egp = order.bedroom_undiscounted * order.additional_currency_rate

    @api.depends('bedroom_discount_amount','additional_currency_rate')
    def _compute_bedroom_discount_amount_egp(self):
        for order in self:
            order.bedroom_discount_amount_egp = order.bedroom_discount_amount * order.additional_currency_rate

    accessory_untaxed_egp = fields.Float('Accessory Untaxed Amount (EGP)', compute='compute_accessory_untaxed_egp')
    accessory_tax_egp = fields.Float('Accessory Tax Amount (EGP)', compute='compute_accessory_untaxed_egp')
    accessory_total_egp = fields.Float('Accessory Total Amount (EGP)', compute='compute_accessory_untaxed_egp')
    accessory_unit_prices_egp = fields.Float('Accessory Unit Prices (EGP)', compute='compute_accessory_untaxed_egp')
    accessory_undiscounted_egp = fields.Float('Amount Before Discount Eg', compute='_compute_accessory_undiscounted_eg', digits=0)
    accessory_discount_amount_egp = fields.Float('Discount Amount Eg', compute='_compute_accessory_discount_amount_egp')

    @api.depends('accessory_undiscounted')
    def _compute_accessory_undiscounted_eg(self):
        for order in self:
            order.accessory_undiscounted_egp = order.accessory_undiscounted * order.additional_currency_rate

    @api.depends('accessory_discount_amount','additional_currency_rate')
    def _compute_accessory_discount_amount_egp(self):
        for order in self:
            order.accessory_discount_amount_egp = order.accessory_discount_amount * order.additional_currency_rate

    mixer_untaxed_egp = fields.Float('Mixer Untaxed Amount (EGP)', compute='compute_mixer_untaxed_egp')
    mixer_tax_egp = fields.Float('Mixer Tax Amount (EGP)', compute='compute_mixer_untaxed_egp')
    mixer_total_egp = fields.Float('Mixer Total Amount (EGP)', compute='compute_mixer_untaxed_egp')
    mixer_unit_prices_egp = fields.Float('Mixer Unit Prices (EGP)', compute='compute_mixer_untaxed_egp')
    mixer_undiscounted_egp = fields.Float('Amount Before Discount Eg', compute='_compute_mixer_undiscounted_eg', digits=0)
    mixer_discount_amount_egp = fields.Float('Discount Amount Eg', compute='_compute_mixer_discount_amount_egp')

    @api.depends('mixer_undiscounted')
    def _compute_mixer_undiscounted_eg(self):
        for order in self:
            order.mixer_undiscounted_egp = order.mixer_undiscounted * order.additional_currency_rate

    @api.depends('mixer_discount_amount','additional_currency_rate')
    def _compute_mixer_discount_amount_egp(self):
        for order in self:
            order.mixer_discount_amount_egp = order.mixer_discount_amount * order.additional_currency_rate

    electronic_untaxed_egp = fields.Float('Electronic Untaxed Amount (EGP)', compute='compute_electronic_untaxed_egp')
    electronic_tax_egp = fields.Float('Electronic Tax Amount (EGP)', compute='compute_electronic_untaxed_egp')
    electronic_total_egp = fields.Float('Electronic Total Amount (EGP)', compute='compute_electronic_untaxed_egp')
    electronic_unit_prices_egp = fields.Float('Electronic Unit Prices (EGP)', compute='compute_electronic_untaxed_egp')
    electronic_undiscounted_egp = fields.Float('Amount Before Discount Eg', compute='_compute_electronic_undiscounted_eg', digits=0)
    electronic_discount_amount_egp = fields.Float('Discount Amount Eg', compute='_compute_electronic_discount_amount_egp')

    @api.depends('electronic_undiscounted')
    def _compute_electronic_undiscounted_eg(self):
        for order in self:
            order.electronic_undiscounted_egp = order.electronic_undiscounted * order.additional_currency_rate

    @api.depends('electronic_discount_amount','additional_currency_rate')
    def _compute_electronic_discount_amount_egp(self):
        for order in self:
            order.electronic_discount_amount_egp = order.electronic_discount_amount * order.additional_currency_rate

    worktop_untaxed_egp = fields.Float('Worktop Untaxed Amount (EGP)', compute='compute_worktop_untaxed_egp')
    worktop_tax_egp = fields.Float('Worktop Tax Amount (EGP)', compute='compute_worktop_untaxed_egp')
    worktop_total_egp = fields.Float('Worktop Total Amount (EGP)', compute='compute_worktop_untaxed_egp')
    worktop_unit_prices_egp = fields.Float('Worktop Unit Prices (EGP)', compute='compute_worktop_untaxed_egp')
    worktop_undiscounted_egp = fields.Float('Amount Before Discount Eg', compute='_compute_worktop_undiscounted_eg', digits=0)
    worktop_discount_amount_egp = fields.Float('Discount Amount Eg', compute='_compute_worktop_discount_amount_egp')

    @api.depends('worktop_undiscounted')
    def _compute_worktop_undiscounted_eg(self):
        for order in self:
            order.worktop_undiscounted_egp = order.worktop_undiscounted * order.additional_currency_rate

    @api.depends('worktop_discount_amount','additional_currency_rate')
    def _compute_worktop_discount_amount_egp(self):
        for order in self:
            order.worktop_discount_amount_egp = order.worktop_discount_amount * order.additional_currency_rate

    service_untaxed_egp = fields.Float('Service Untaxed Amount (EGP)', compute='compute_service_untaxed_egp')
    service_tax_egp = fields.Float('Service Tax Amount (EGP)', compute='compute_service_untaxed_egp')
    service_total_egp = fields.Float('Service Total Amount (EGP)', compute='compute_service_untaxed_egp')
    service_unit_prices_egp = fields.Float('Service Unit Prices (EGP)', compute='compute_service_untaxed_egp')
    service_undiscounted_egp = fields.Float('Amount Before Discount Eg', compute='_compute_service_undiscounted_eg', digits=0)
    service_discount_amount_egp = fields.Float('Discount Amount Eg', compute='_compute_service_discount_amount_egp')

    @api.depends('service_undiscounted')
    def _compute_service_undiscounted_eg(self):
        for order in self:
            order.service_undiscounted_egp = order.service_undiscounted * order.additional_currency_rate

    @api.depends('service_discount_amount','additional_currency_rate')
    def _compute_service_discount_amount_egp(self):
        for order in self:
            order.service_discount_amount_egp = order.service_discount_amount * order.additional_currency_rate

    appliance_untaxed_egp = fields.Float('Appliance Untaxed Amount (EGP)', compute='compute_appliance_untaxed_egp')
    appliance_tax_egp = fields.Float('Appliance Tax Amount (EGP)', compute='compute_appliance_untaxed_egp')
    appliance_total_egp = fields.Float('Appliance Total Amount (EGP)', compute='compute_appliance_untaxed_egp')
    appliance_unit_prices_egp = fields.Float('Appliance Unit Prices (EGP)', compute='compute_appliance_untaxed_egp')
    appliance_undiscounted_egp = fields.Float('Amount Before Discount Eg', compute='_compute_appliance_undiscounted_eg', digits=0)
    appliance_discount_amount_egp = fields.Float('Discount Amount Eg', compute='_compute_appliance_discount_amount_egp')

    @api.depends('appliance_undiscounted')
    def _compute_appliance_undiscounted_eg(self):
        for order in self:
            order.appliance_undiscounted_egp = order.appliance_undiscounted * order.additional_currency_rate

    @api.depends('appliance_discount_amount','additional_currency_rate')
    def _compute_appliance_discount_amount_egp(self):
        for order in self:
            order.appliance_discount_amount_egp = order.appliance_discount_amount * order.additional_currency_rate

    show_discount = fields.Boolean(string='Show Discount')
    discount_amount = fields.Float(string='Discount Amount', compute='_compute_discount_amount',digits=0)
    amount_undiscounted_eg = fields.Float('Amount Before Discount Eg', compute='_compute_amount_undiscounted_eg', digits=0)
    discount_amount_other = fields.Float(string='Discount Amount', compute='_compute_discount_amount_other',digits=0)


    # @api.depends('amount_total','order_line.discount')
    # def _compute_discount_amount(self):
    #     for order in self:
    #         order.discount_amount = order.amount_undiscounted - order.amount_total
    #         print(order.discount_amount)


    @api.depends('amount_undiscounted')
    def _compute_amount_undiscounted_eg(self):
        for order in self:
            order.amount_undiscounted_eg = order.amount_undiscounted * order.additional_currency_rate

    @api.depends('amount_total', 'order_line.discount','additional_currency_rate','amount_tax','amount_undiscounted')
    def _compute_discount_amount(self):
        for order in self:
            order.discount_amount =(order.amount_undiscounted * order.additional_currency_rate - order.amount_total * order.additional_currency_rate) + (order.amount_tax * order.additional_currency_rate)
            print(order.discount_amount)
            print(order.amount_tax)

    @api.depends('amount_total', 'order_line.discount','amount_tax','amount_undiscounted')
    def _compute_discount_amount_other(self):
        for order in self:
            order.discount_amount_other = (order.amount_undiscounted - order.amount_total) + order.amount_tax




    @api.depends('wood_untaxed', 'wood_tax', 'wood_total', 'additional_currency_rate')
    def compute_wood_untaxed_egp(self):
        for order in self:
            order.wood_untaxed_egp = order.wood_untaxed * order.additional_currency_rate
            order.wood_tax_egp = order.wood_tax * order.additional_currency_rate
            order.wood_unit_prices_egp = order.wood_unit_prices * order.additional_currency_rate
            order.wood_total_egp = order.wood_total * order.additional_currency_rate

    @api.depends('bedroom_untaxed', 'bedroom_tax', 'bedroom_total', 'additional_currency_rate')
    def compute_bedroom_untaxed_egp(self):
        for order in self:
            order.bedroom_untaxed_egp = order.bedroom_untaxed * order.additional_currency_rate
            order.bedroom_tax_egp = order.bedroom_tax * order.additional_currency_rate
            order.bedroom_unit_prices_egp = order.bedroom_unit_prices * order.additional_currency_rate
            order.bedroom_total_egp = order.bedroom_total * order.additional_currency_rate

    @api.depends('accessory_untaxed', 'accessory_tax', 'accessory_total', 'additional_currency_rate')
    def compute_accessory_untaxed_egp(self):
        for order in self:
            order.accessory_untaxed_egp = order.accessory_untaxed * order.additional_currency_rate
            order.accessory_tax_egp = order.accessory_tax * order.additional_currency_rate
            order.accessory_unit_prices_egp = order.accessory_unit_prices * order.additional_currency_rate
            order.accessory_total_egp = order.accessory_total * order.additional_currency_rate

    @api.depends('mixer_untaxed', 'mixer_tax', 'mixer_total', 'additional_currency_rate')
    def compute_mixer_untaxed_egp(self):
        for order in self:
            order.mixer_untaxed_egp = order.mixer_untaxed * order.additional_currency_rate
            order.mixer_tax_egp = order.mixer_tax * order.additional_currency_rate
            order.mixer_unit_prices_egp = order.mixer_unit_prices * order.additional_currency_rate
            order.mixer_total_egp = order.mixer_total * order.additional_currency_rate

    @api.depends('electronic_untaxed', 'electronic_tax', 'electronic_total', 'additional_currency_rate')
    def compute_electronic_untaxed_egp(self):
        for order in self:
            order.electronic_untaxed_egp = order.electronic_untaxed * order.additional_currency_rate
            order.electronic_tax_egp = order.electronic_tax * order.additional_currency_rate
            order.electronic_unit_prices_egp = order.electronic_unit_prices * order.additional_currency_rate
            order.electronic_total_egp = order.electronic_total * order.additional_currency_rate

    @api.depends('worktop_untaxed', 'worktop_tax', 'worktop_total', 'additional_currency_rate')
    def compute_worktop_untaxed_egp(self):
        for order in self:
            order.worktop_untaxed_egp = order.worktop_untaxed * order.additional_currency_rate
            order.worktop_tax_egp = order.worktop_tax * order.additional_currency_rate
            order.worktop_unit_prices_egp = order.worktop_unit_prices * order.additional_currency_rate
            order.worktop_total_egp = order.worktop_total * order.additional_currency_rate

    @api.depends('service_untaxed', 'service_tax', 'service_total', 'additional_currency_rate')
    def compute_service_untaxed_egp(self):
        for order in self:
            order.service_untaxed_egp = order.service_untaxed * order.additional_currency_rate
            order.service_tax_egp = order.service_tax * order.additional_currency_rate
            order.service_unit_prices_egp = order.service_unit_prices * order.additional_currency_rate
            order.service_total_egp = order.service_total * order.additional_currency_rate

    @api.depends('appliance_untaxed', 'appliance_tax', 'appliance_total', 'additional_currency_rate')
    def compute_appliance_untaxed_egp(self):
        for order in self:
            order.appliance_untaxed_egp = order.appliance_untaxed * order.additional_currency_rate
            order.appliance_tax_egp = order.appliance_tax * order.additional_currency_rate
            order.appliance_unit_prices_egp = order.appliance_unit_prices * order.additional_currency_rate
            order.appliance_total_egp = order.appliance_total * order.additional_currency_rate
    @api.depends('wood_order_line')
    def _compute_wood_totals(self):
        for rec in self:
            rec.wood_untaxed = sum(rec.wood_order_line.mapped('price_subtotal'))
            rec.wood_tax = sum(rec.wood_order_line.mapped('price_tax'))
            rec.wood_unit_prices = sum(rec.wood_order_line.mapped(lambda x: x.price_unit * x.product_uom_qty))
            rec.wood_total = rec.wood_untaxed + rec.wood_tax

    def _compute_wood_undiscounted(self):
        for order in self:
            total = 0.0
            for line in order.wood_order_line:

                total += (line.price_subtotal * 100)/(100-line.discount) if line.discount != 100 else (line.price_unit * line.product_uom_qty)
            order.wood_undiscounted = total

    @api.depends('wood_order_line.discount', 'wood_undiscounted','wood_tax','wood_total')
    def _compute_wood_discount_amount(self):
        for order in self:
            order.wood_discount_amount = (order.wood_undiscounted - order.wood_total) + order.wood_tax

    @api.depends('accessory_order_line')
    def _compute_accessory_totals(self):
        for rec in self:
            rec.accessory_untaxed = sum(rec.accessory_order_line.mapped('price_subtotal'))
            rec.accessory_tax = sum(rec.accessory_order_line.mapped('price_tax'))
            rec.accessory_unit_prices = sum(rec.accessory_order_line.mapped(lambda x: x.price_unit * x.product_uom_qty))
            rec.accessory_total = rec.accessory_untaxed + rec.accessory_tax

    def _compute_accessory_undiscounted(self):
        for order in self:
            total = 0.0
            for line in order.accessory_order_line:

                total += (line.price_subtotal * 100)/(100-line.discount) if line.discount != 100 else (line.price_unit * line.product_uom_qty)
            order.accessory_undiscounted = total

    @api.depends('accessory_order_line.discount', 'accessory_undiscounted','accessory_tax','accessory_total')
    def _compute_accessory_discount_amount(self):
        for order in self:
            order.accessory_discount_amount = (order.accessory_undiscounted - order.accessory_total) + order.accessory_tax

    @api.depends('mixer_order_line')
    def _compute_mixer_totals(self):
        for rec in self:
            rec.mixer_untaxed = sum(rec.mixer_order_line.mapped('price_subtotal'))
            rec.mixer_tax = sum(rec.mixer_order_line.mapped('price_tax'))
            rec.mixer_unit_prices = sum(rec.mixer_order_line.mapped(lambda x: x.price_unit * x.product_uom_qty))
            rec.mixer_total = rec.mixer_untaxed + rec.mixer_tax

    def _compute_mixer_undiscounted(self):
        for order in self:
            total = 0.0
            for line in order.mixer_order_line:

                total += (line.price_subtotal * 100)/(100-line.discount) if line.discount != 100 else (line.price_unit * line.product_uom_qty)
            order.mixer_undiscounted = total

    @api.depends('mixer_order_line.discount', 'mixer_undiscounted','mixer_tax','mixer_total')
    def _compute_mixer_discount_amount(self):
        for order in self:
            order.mixer_discount_amount = (order.mixer_undiscounted - order.mixer_total) + order.mixer_tax

    @api.depends('electronic_order_line')
    def _compute_electronic_totals(self):
        for rec in self:
            rec.electronic_untaxed = sum(rec.electronic_order_line.mapped('price_subtotal'))
            rec.electronic_tax = sum(rec.electronic_order_line.mapped('price_tax'))
            rec.electronic_unit_prices = sum(rec.electronic_order_line.mapped(lambda x: x.price_unit * x.product_uom_qty))
            rec.electronic_total = rec.electronic_untaxed + rec.electronic_tax

    def _compute_electronic_undiscounted(self):
        for order in self:
            total = 0.0
            for line in order.electronic_order_line:

                total += (line.price_subtotal * 100)/(100-line.discount) if line.discount != 100 else (line.price_unit * line.product_uom_qty)
            order.electronic_undiscounted = total

    @api.depends('electronic_order_line.discount', 'electronic_undiscounted','electronic_tax','electronic_total')
    def _compute_electronic_discount_amount(self):
        for order in self:
            order.electronic_discount_amount = (order.electronic_undiscounted - order.electronic_total) + order.electronic_tax

    @api.depends('worktop_order_line')
    def _compute_worktop_totals(self):
        for rec in self:
            rec.worktop_untaxed = sum(rec.worktop_order_line.mapped('price_subtotal'))
            rec.worktop_tax = sum(rec.worktop_order_line.mapped('price_tax'))
            rec.worktop_unit_prices = sum(rec.worktop_order_line.mapped(lambda x: x.price_unit * x.product_uom_qty))
            rec.worktop_total = rec.worktop_untaxed + rec.worktop_tax

    def _compute_worktop_undiscounted(self):
        for order in self:
            total = 0.0
            for line in order.worktop_order_line:

                total += (line.price_subtotal * 100)/(100-line.discount) if line.discount != 100 else (line.price_unit * line.product_uom_qty)
            order.worktop_undiscounted = total

    @api.depends('worktop_order_line.discount', 'worktop_undiscounted','worktop_tax','worktop_total')
    def _compute_worktop_discount_amount(self):
        for order in self:
            order.worktop_discount_amount = (order.worktop_undiscounted - order.worktop_total) + order.worktop_tax

    @api.depends('service_order_line')
    def _compute_service_totals(self):
        for rec in self:
            rec.service_untaxed = sum(rec.service_order_line.mapped('price_subtotal'))
            rec.service_tax = sum(rec.service_order_line.mapped('price_tax'))
            rec.service_unit_prices = sum(rec.service_order_line.mapped(lambda x: x.price_unit * x.product_uom_qty))
            rec.service_total = rec.service_untaxed + rec.service_tax

    def _compute_service_undiscounted(self):
        for order in self:
            total = 0.0
            for line in order.service_order_line:

                total += (line.price_subtotal * 100)/(100-line.discount) if line.discount != 100 else (line.price_unit * line.product_uom_qty)
            order.service_undiscounted = total


    @api.depends('service_order_line.discount', 'service_undiscounted','service_tax','service_total')
    def _compute_service_discount_amount(self):
        for order in self:
            order.service_discount_amount = (order.service_undiscounted - order.service_total) + order.service_tax

    @api.depends('appliance_order_line')
    def _compute_appliance_totals(self):
        for rec in self:
            rec.appliance_untaxed = sum(rec.appliance_order_line.mapped('price_subtotal'))
            rec.appliance_tax = sum(rec.appliance_order_line.mapped('price_tax'))
            rec.appliance_unit_prices = sum(rec.appliance_order_line.mapped(lambda x: x.price_unit * x.product_uom_qty))
            rec.appliance_total = rec.appliance_untaxed + rec.appliance_tax

    def _compute_appliance_undiscounted(self):
        for order in self:
            total = 0.0
            for line in order.appliance_order_line:

                total += (line.price_subtotal * 100)/(100-line.discount) if line.discount != 100 else (line.price_unit * line.product_uom_qty)
            order.appliance_undiscounted = total

    @api.depends('appliance_order_line.discount', 'appliance_undiscounted','appliance_tax','appliance_total')
    def _compute_appliance_discount_amount(self):
        for order in self:
            order.appliance_discount_amount = (order.appliance_undiscounted - order.appliance_total) + order.appliance_tax

    @api.depends('bedroom_order_line')
    def _compute_bedroom_totals(self):
        for rec in self:
            rec.bedroom_untaxed = sum(rec.bedroom_order_line.mapped('price_subtotal'))
            rec.bedroom_tax = sum(rec.bedroom_order_line.mapped('price_tax'))
            rec.bedroom_unit_prices = sum(rec.bedroom_order_line.mapped(lambda x: x.price_unit * x.product_uom_qty))
            rec.bedroom_total = rec.bedroom_untaxed + rec.bedroom_tax

    def _compute_bedroom_undiscounted(self):
        for order in self:
            total = 0.0
            for line in order.bedroom_order_line:

                total += (line.price_subtotal * 100)/(100-line.discount) if line.discount != 100 else (line.price_unit * line.product_uom_qty)
            order.bedroom_undiscounted = total

    @api.depends('bedroom_order_line.discount', 'bedroom_undiscounted','bedroom_tax','bedroom_total')
    def _compute_bedroom_discount_amount(self):
        for order in self:
            order.bedroom_discount_amount = (order.bedroom_undiscounted - order.bedroom_total) + order.bedroom_tax

    @api.onchange('company_id')
    def _onchange_company_id(self):
        super(SaleOrder, self)._onchange_company_id()
        self.warehouse_id = False
        # if self.company_id:
        #     warehouse_id = self.env['ir.default'].get_model_defaults('sale.order').get('warehouse_id')
        #     self.warehouse_id = warehouse_id or self.user_id.with_company(self.company_id.id)._get_default_warehouse_id().id

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.state in ['draft', 'sent']:
            self.warehouse_id = False
        # if self.state in ['draft', 'sent']:
        # self.warehouse_id = self.user_id.with_company(self.company_id.id)._get_default_warehouse_id().id

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        sp_id, st_id = self.user_id.id, self.team_id.id
        self.update({'user_id': sp_id, 'team_id': st_id, })

    def action_set_discount(self):
        action = self.sudo().env.ref('hz_sale_custom.action_set_discount').read()[0]
        return action

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(SaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                        submenu=submenu)
        cannot_create = not self.env.user.has_group('hz_sale_custom.group_sale_create')
        if cannot_create and not self._context.get('creating_from_crm', False):
            doc = etree.XML(result['arch'])
            for node in doc.xpath("//tree") + doc.xpath("//form") + doc.xpath("//kanban"):
                node.set('create', '0')
            result['arch'] = etree.tostring(doc, encoding='unicode')
        return result

    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):

        if not self.sale_order_template_id:
            # self.require_signature = self._get_default_require_signature()
            # self.require_payment = self._get_default_require_payment()
            return

        template = self.sale_order_template_id.with_context(lang=self.partner_id.lang)

        # --- first, process the list of products from the template
        # Preserve existing order lines
        order_lines = [(1, line.id, {}) for line in self.order_line]  # Keep existing lines without modification

        for line in template.sale_order_template_line_ids:
            data = self._compute_line_data_for_template_change(line)

            if line.product_id:
                price = line.product_id.lst_price
                discount = 0

                if self.pricelist_id:
                    pricelist_price = self.pricelist_id.with_context(uom=line.product_uom_id.id).get_product_price(
                        line.product_id, 1, False)

                    if self.pricelist_id.discount_policy == 'without_discount' and price:
                        discount = max(0, (price - pricelist_price) * 100 / price)
                    else:
                        price = pricelist_price

                data.update({
                    'price_unit': price,
                    'discount': discount,
                    'product_uom_qty': line.product_uom_qty,
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_uom_id.id,
                    'customer_lead': self._get_customer_lead(line.product_id.product_tmpl_id),
                })

            order_lines.append((0, 0, data))

        # Set first line from new lines to sequence -99 if any new lines are added
        if len(template.sale_order_template_line_ids) > 0:
            order_lines[-len(template.sale_order_template_line_ids)][2]['sequence'] = -99

        self.order_line = order_lines
        self.order_line._compute_tax_id()

        # then, process the list of optional products from the template
        option_lines = [(5, 0, 0)]
        for option in template.sale_order_template_option_ids:
            data = self._compute_option_data_for_template_change(option)
            option_lines.append((0, 0, data))

        self.sale_order_option_ids = option_lines

        if template.number_of_days > 0:
            self.validity_date = fields.Date.context_today(self) + timedelta(template.number_of_days)

        self.require_signature = template.require_signature
        self.require_payment = template.require_payment

        if not is_html_empty(template.note):
            self.note = template.note




class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_tax_readonly_sale = fields.Boolean(string='Readonly Tax', related='company_id.is_tax_readonly_sale')
    is_sol_price_editable = fields.Boolean(
        "Editable unit price", related='company_id.is_sol_price_editable')
    is_sol_discount_editable = fields.Boolean(
        "Editable Discount", related='company_id.is_sol_discount_editable')
    product_categ_id = fields.Many2one('product.category', related='product_id.categ_id', store=True)
    price_unit_egp = fields.Float('Unit Price (EGP)', compute='compute_price_unit_egp')
    categ_type = fields.Selection([('all', 'All'),
                                   ('wood', 'Wood'),
                                   ('accessory', 'Accessory'),
                                   ('mixer', 'Mixer'),
                                   ('electronic', 'Electronic'),
                                   ('worktop', 'Worktop'),
                                   ('service', 'Service'),
                                   ('appliance', 'Appliance'),
                                   ('bedroom', 'Bedroom'),
                                   ], store=True, compute='_compute_categ_type')

    @api.depends('price_subtotal', 'price_tax', 'order_id.additional_currency_rate')
    def compute_price_unit_egp(self):
        for line in self:
            # Get the rate or default to 1.0 to prevent errors
            rate = line.order_id.additional_currency_rate or 1.0

            # Check if an additional currency is actually set
            if line.order_id.additional_currency:
                line.price_subtotal_egp = line.price_subtotal * rate
                line.price_tax_egp = line.price_tax * rate
            else:
                # ESSENTIAL: Assign default values if condition is not met
                line.price_subtotal_egp = line.price_subtotal
                line.price_tax_egp = line.price_tax



    @api.depends('order_id.is_separate_sol', 'product_categ_id',
                 'order_id.wood_categs',
                 'order_id.accessory_categs',
                 'order_id.mixer_categs',
                 'order_id.electronic_categs',
                 'order_id.worktop_categs',
                 'order_id.service_categs',
                 'order_id.appliance_categs',
                 'order_id.bedroom_categs',
                 )
    def _compute_categ_type(self):
        for rec in self:
            rec.categ_type = 'all'
            if rec.order_id.is_separate_sol:
                if rec.product_categ_id.id in rec.order_id.wood_categs.ids:
                    rec.categ_type = 'wood'
                elif rec.product_categ_id.id in rec.order_id.accessory_categs.ids:
                    rec.categ_type = 'accessory'
                elif rec.product_categ_id.id in rec.order_id.mixer_categs.ids:
                    rec.categ_type = 'mixer'
                elif rec.product_categ_id.id in rec.order_id.electronic_categs.ids:
                    rec.categ_type = 'electronic'
                elif rec.product_categ_id.id in rec.order_id.worktop_categs.ids:
                    rec.categ_type = 'worktop'
                elif rec.product_categ_id.id in rec.order_id.service_categs.ids:
                    rec.categ_type = 'service'
                elif rec.product_categ_id.id in rec.order_id.appliance_categs.ids:
                    rec.categ_type = 'appliance'
                elif rec.product_categ_id.id in rec.order_id.bedroom_categs.ids:
                    rec.categ_type = 'bedroom'
