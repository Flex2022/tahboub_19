# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class SaleGetProduct(models.TransientModel):
    _name = 'sale.get.product'
    _description = 'Get products from sale order'

    sale_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', required=True)
    line_ids = fields.One2many('sale.get.product.line', 'wizard_id', string='Lines')

    @api.onchange('sale_id')
    def onchange_sale_id(self):
        self.line_ids = [(5, 0, 0)]
        if self.sale_id:
            lines_mrp_ok = self.sale_id.order_line.filtered(
                lambda l: l.product_id and l.product_id.mrp_ok and l.product_id != self.production_id.product_id)
            self.line_ids = [(0, 0, {'product_id': l.product_id.id,
                                     'qty': l.product_uom_qty,
                                     'product_uom': l.product_uom.id,
                                     }) for l in lines_mrp_ok]

    def action_confirm(self):
        lines = [{'product_id': line.product_id.id,
                  'product_uom_qty': line.qty,
                  'product_uom': line.product_uom.id,
                  # 'product_uom': l.product_id.uom_id.id,
                  'name': line.product_id.partner_ref,
                  'date': self.production_id.date_planned_finished,
                  'date_deadline': self.production_id.date_deadline,
                  'location_id': self.production_id.production_location_id.id,
                  'location_dest_id': self.production_id.location_dest_id.id,
                  'state': 'draft',
                  'production_id': self.production_id.id,
                  'picking_type_id': self.production_id.picking_type_id.id,
                  'company_id': self.production_id.company_id.id,
                  } for line in self.line_ids]
        self.production_id.move_byproduct_ids.create(lines)


class SaleGetProductLine(models.TransientModel):
    _name = 'sale.get.product.line'
    _description = 'Get product line'

    wizard_id = fields.Many2one('sale.get.product', string='Wizard')
    mrp_product_id = fields.Many2one('product.product', string='MRP Product', related='wizard_id.production_id.product_id')
    product_id = fields.Many2one('product.product', string='Product', required=True,
                                 domain="[('mrp_ok', '=', True), ('id', '!=', mrp_product_id)]")
    qty = fields.Float(string='Quantity')
    product_uom = fields.Many2one('uom.uom', "UoM", required=True, readonly=True)


    @api.constrains('qty')
    def onchange_sale_id(self):
        if self.filtered(lambda l: not l.qty > 0):
            raise ValidationError('Quantity must be positive.')
