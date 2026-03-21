# -*- coding: utf-8 -*-
from collections import Counter

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    lot_subserial_id = fields.Many2one(
        "stock.lot.subserial",
        string="Sub Serial",
        copy=False,
        check_company=True,
        domain="[('lot_id', '=', lot_id), ('state', '=', 'available')]",
    )

    @api.onchange("lot_id")
    def _onchange_lot_id_reset_subserial(self):
        for line in self:
            if line.lot_subserial_id and line.lot_subserial_id.lot_id != line.lot_id:
                line.lot_subserial_id = False

    @api.onchange("lot_subserial_id")
    def _onchange_lot_subserial_id(self):
        for line in self:
            if line.lot_subserial_id and not line.lot_id:
                line.lot_id = line.lot_subserial_id.lot_id

    @api.constrains("lot_subserial_id", "lot_id", "product_id")
    def _check_lot_subserial_consistency(self):
        for line in self.filtered("lot_subserial_id"):
            if not line.lot_id:
                raise ValidationError(_("You must select a Lot before selecting a Sub Serial."))
            if line.lot_subserial_id.lot_id != line.lot_id:
                raise ValidationError(
                    _(
                        "Sub Serial %(sub_serial)s does not belong to Lot %(lot)s.",
                        sub_serial=line.lot_subserial_id.name,
                        lot=line.lot_id.name,
                    )
                )
            if line.product_id and line.lot_subserial_id.product_id and line.product_id != line.lot_subserial_id.product_id:
                raise ValidationError(
                    _(
                        "Sub Serial %(sub_serial)s is not valid for product %(product)s.",
                        sub_serial=line.lot_subserial_id.name,
                        product=line.product_id.display_name,
                    )
                )

    @api.constrains("lot_subserial_id", "qty_done", "product_uom_id")
    def _check_lot_subserial_qty(self):
        for line in self.filtered("lot_subserial_id"):
            if float_compare(line.qty_done, 1.0, precision_rounding=line.product_uom_id.rounding) > 0:
                raise ValidationError(
                    _(
                        "Sub Serial %(sub_serial)s can only be used with quantity 1 per operation line.",
                        sub_serial=line.lot_subserial_id.name,
                    )
                )

    def _action_done(self):
        lines_with_subserial = self.filtered(
            lambda ml: ml.lot_subserial_id
            and float_compare(ml.qty_done, 0.0, precision_rounding=ml.product_uom_id.rounding) > 0
        )
        to_customer_lines = lines_with_subserial.filtered(
            lambda ml: ml.location_dest_id.usage == "customer" and ml.location_id.usage in ("internal", "transit")
        )
        duplicate_counter = Counter([line.lot_subserial_id.id for line in to_customer_lines])
        duplicate_ids = [subserial_id for subserial_id, count in duplicate_counter.items() if count > 1]
        if duplicate_ids:
            duplicate_names = ", ".join(
                self.env["stock.lot.subserial"].browse(duplicate_ids).mapped("display_name")
            )
            raise ValidationError(
                _("You cannot use the same Sub Serial more than once in the same transfer: %s")
                % duplicate_names
            )

        for line in to_customer_lines:
            if line.lot_subserial_id.state != "available" and line.lot_subserial_id.used_move_line_id != line:
                raise ValidationError(
                    _(
                        "Sub Serial %(sub_serial)s is already used in transfer %(picking)s.",
                        sub_serial=line.lot_subserial_id.display_name,
                        picking=line.lot_subserial_id.used_picking_id.display_name or "-",
                    )
                )

        res = super()._action_done()

        processed_lines = self.filtered(
            lambda ml: ml.exists()
            and ml.lot_subserial_id
            and float_compare(ml.qty_done, 0.0, precision_rounding=ml.product_uom_id.rounding) > 0
        )

        done_to_customer_lines = processed_lines.filtered(
            lambda ml: ml.location_dest_id.usage == "customer" and ml.location_id.usage in ("internal", "transit")
        )
        for line in done_to_customer_lines:
            line.lot_subserial_id.sudo().write(
                {
                    "state": "used",
                    "used_move_line_id": line.id,
                }
            )

        customer_return_lines = processed_lines.filtered(
            lambda ml: ml.location_id.usage == "customer" and ml.location_dest_id.usage in ("internal", "transit")
        )
        for line in customer_return_lines:
            line.lot_subserial_id.sudo().write(
                {
                    "state": "available",
                    "used_move_line_id": False,
                }
            )

        return res
