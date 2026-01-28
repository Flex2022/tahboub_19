# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    product_id = fields.Many2one('product.product', required=False)
    product_uom = fields.Many2one('uom.uom', required=False)
    service_no = fields.Char(string='Service Number', required=False, indexe=True)
    guarantee_limit = fields.Date('Warranty Expiration')

    # _sql_constraints = [('service_no_unique', 'unique (service_no)', 'Service number must be unique')]

    def action_validate(self):
        if self.filtered(lambda repair: not (repair.product_id and repair.product_uom)):
            raise UserError(_("Please set product and uom before confirmation."))
        return super(RepairOrder, self).action_validate()

    def action_repair_confirm(self):
        if self.filtered(lambda repair: not (repair.product_id and repair.product_uom)):
            raise UserError(_("Please set product and uom before confirmation."))
        return super(RepairOrder, self).action_repair_confirm()

class RepairLine(models.Model):
    _inherit = 'stock.move'

    @api.onchange('type')
    def onchange_operation_type(self):
        for line in self:
            args = line.repair_id.company_id and [('company_id', '=', line.repair_id.company_id.id)] or []
            warehouse = line.env['stock.warehouse'].search(args, limit=1)

            if not line.type:
                line.location_id = False
                line.location_dest_id = False
            elif line.type == 'add':
                line.location_id = warehouse.lot_stock_id
                line.location_dest_id = line.env['stock.location'].search(
                    [('usage', '=', 'customer'), '|', ('company_id', '=', line.repair_id.company_id.id),
                     ('company_id', '=', False)], limit=1)
            else:
                line.location_id = warehouse.lot_stock_id
                line.location_dest_id = line.env['stock.location'].search(
                    [('scrap_location', '=', True), ('company_id', 'in', [line.repair_id.company_id.id, False])],
                    limit=1).id