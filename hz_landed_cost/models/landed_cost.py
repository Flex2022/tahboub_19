# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError


NEW_SPLIT_METHOD = [
    ('equal', 'Equal'),
    ('by_quantity', 'By Quantity'),
    ('by_current_cost_price', 'By Current Cost'),
    ('by_weight', 'By Weight'),
    ('by_volume', 'By Volume'),
    ('some_products', 'Some Products'),
]


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def compute_landed_cost(self):
        res = super(StockLandedCost, self).compute_landed_cost()

        for cost in self.filtered(lambda cost: cost._get_targeted_move_ids()):
            rounding = cost.currency_id.rounding
            for valuation in cost.valuation_adjustment_lines:
                cost_line = valuation.cost_line_id
                split_method = cost_line.split_method
                by_products = cost_line.by_products
                if split_method == 'some_products':
                    if valuation.product_id.id not in by_products.ids:
                        valuation.unlink()
                        continue
                    value = self._get_landed_cost_some_products(valuation, cost_line)
                    if rounding:
                        # value = tools.float_round(value, precision_rounding=rounding, rounding_method='UP')
                        value = tools.float_round(value, precision_rounding=rounding, rounding_method='HALF-UP')
                    valuation.write({'additional_landed_cost': value})
            self._check_distribution_mistakes()
        return res

    def _check_distribution_mistakes(self):
        for cost_line in self.cost_lines:
            valuation_lines = self.env['stock.valuation.adjustment.lines'].search([('cost_line_id', '=', cost_line.id)])
            additional_landed_cost_per_cost_line = sum(valuation_lines.mapped('additional_landed_cost'))
            diff = cost_line.price_unit - additional_landed_cost_per_cost_line
            if diff != 0:
                valuation_lines[-1].additional_landed_cost += diff

    def _get_landed_cost_some_products(self, valuation_line, cost_line):
        product_ids = cost_line.by_products.ids
        cost_valuation_lines = self.valuation_adjustment_lines.filtered(
            lambda vl: vl.cost_line_id.id == cost_line.id and vl.product_id.id in product_ids)
        total = sum(cost_valuation_lines.mapped('former_cost'))
        return (valuation_line.former_cost / total) * cost_line.price_unit

    def _get_valid_product_ids(self):
        product_ids = []
        if self.target_model == 'picking':
            stock_moves = self.picking_ids.mapped(
                'move_ids_without_package').filtered(lambda m: m.state != 'cancel' and m.product_qty)
            product_ids = stock_moves.mapped('product_id').filtered(lambda p: p.cost_method in ('fifo', 'average')).ids
        elif self.target_model == 'manufacturing':
            stock_moves = self.mrp_production_ids.mapped(
                'move_finished_ids').filtered(lambda m: m.state != 'cancel' and m.product_qty)
            product_ids = stock_moves.mapped('product_id').filtered(lambda p: p.cost_method in ('fifo', 'average')).ids
        return product_ids


class StockLandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    split_method = fields.Selection(NEW_SPLIT_METHOD)
    by_products = fields.Many2many('product.product', 'landed_cost_line_product_rel', string="Products",
                                   domain="[('id', 'in', valid_products)]")
    valid_products = fields.Many2many('product.product', 'landed_cost_line_valid_product_rel', readonly=True,
                                      store=False, string="Valid Products", compute="_get_valid_products")

    @api.depends('cost_id.picking_ids', 'cost_id.target_model')
    def _get_valid_products(self):
        for rec in self:
            valid_product_ids = rec.cost_id._get_valid_product_ids()
            rec.valid_products = valid_product_ids

