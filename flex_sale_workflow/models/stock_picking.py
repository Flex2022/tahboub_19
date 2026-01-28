# -*- coding: utf-8 -*-
from odoo.exceptions import UserError

from odoo import api, fields, models, _, tools
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_partner_id = fields.Many2one('res.partner', related='sale_id.partner_id')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    employee_id = fields.Many2one('hr.employee', string='Responsible Employee')

    # def button_validate(self):
    #     for picking in self.filtered(lambda p: p.picking_type_code == 'outgoing'):
    #         backorder_lines = []
    #         for move in picking.move_lines:
    #             if not move.sale_line_id.flex_is_deliver:
    #                 backorder_lines.append(move.id)
    #
    #         if backorder_lines:
    #             picking._flex_create_backorder(backorder_lines)
    #
    #     return super(StockPicking, self).button_validate()

    def _flex_create_backorder(self, backorder_lines):
        backorders = self.env['stock.picking']
        bo_to_assign = self.env['stock.picking']

        # get lines to backorder
        moves_to_backorder = self.move_ids.filtered(
            lambda x: x.state not in ('done', 'cancel') and x.id in backorder_lines)

        # test if exist lines to backorder
        if moves_to_backorder:
            # create a copy
            backorder_picking = self.copy({
                'name': '/',
                'move_ids': [],
                'move_line_ids': [],
                'backorder_id': self.id
            })

            # create a message post
            self.message_post(
                body=_(
                    'The backorder <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (
                         backorder_picking.id, backorder_picking.name))
            # write on some fields
            moves_to_backorder.write({'picking_id': backorder_picking.id})
            moves_to_backorder.move_line_ids.package_level_id.write({'picking_id': backorder_picking.id})
            moves_to_backorder.mapped('move_line_ids').write({'picking_id': backorder_picking.id})
            backorders |= backorder_picking
            if backorder_picking.picking_type_id.reservation_method == 'at_confirm':
                bo_to_assign |= backorder_picking

        # assign if there are lines to assign
        if bo_to_assign:
            bo_to_assign.action_assign()
        return backorders

class StockMove(models.Model):
    _inherit = 'stock.move'

    picking_type_code = fields.Selection(related='picking_id.picking_type_code')

    # @api.model
    # def create(self, vals):
    #     res = super(StockMove, self).create(vals)
    #     for rec in res:
    #         if rec.picking_id and rec.picking_type_code != 'internal':
    #             raise UserError("Cannot create stock moves for non-incoming pickings.")
    #
    #     return res
    #
    #
    # def write(self, vals):
    #     for rec in self:
    #         if 'picking_id' in vals:
    #             picking = self.env['stock.picking'].browse(vals['picking_id'])
    #             if picking.picking_type_code != 'internal':
    #                 raise UserError("Cannot change picking to a non-incoming type.")
    #     return super(StockMove, self).write(vals)

# class StockMoveLine(models.Model):
#     _inherit = 'stock.move.line'
#
#
#     @api.model
#     def create(self, vals):
#         res = super(StockMove, self).create(vals)
#         for rec in res:
#             if rec.picking_id and rec.picking_code != 'internal':
#                 raise UserError("Cannot create stock moves Lines for non-incoming pickings.")
#
#         return res
#
#     def write(self, vals):
#         for rec in self:
#             if 'picking_id' in vals:
#                 picking = self.env['stock.picking'].browse(vals['picking_id'])
#                 if picking.picking_code != 'internal':
#                     raise UserError("Cannot change picking to a non-incoming type.")
#         return super(StockMoveLine, self).write(vals)
