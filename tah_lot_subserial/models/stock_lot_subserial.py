# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockLotSubSerial(models.Model):
    _name = "stock.lot.subserial"
    _description = "Lot Sub Serial"
    _order = "lot_id, name, id"

    name = fields.Char(required=True, index=True)
    lot_id = fields.Many2one(
        "stock.lot",
        string="Lot",
        required=True,
        index=True,
        ondelete="cascade",
        check_company=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        related="lot_id.product_id",
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="lot_id.company_id",
        store=True,
        readonly=True,
    )
    state = fields.Selection(
        [("available", "Available"), ("used", "Used")],
        default="available",
        required=True,
        readonly=True,
    )
    used_move_line_id = fields.Many2one(
        "stock.move.line",
        string="Used Move Line",
        readonly=True,
        copy=False,
    )
    used_picking_id = fields.Many2one(
        "stock.picking",
        string="Used Transfer",
        related="used_move_line_id.picking_id",
        store=True,
        readonly=True,
    )

    _sql_constraints = [
        (
            "lot_subserial_unique_per_lot",
            "unique(lot_id, name)",
            "Sub-Serial must be unique inside the same Lot.",
        ),
    ]

    @api.model
    def name_create(self, name):
        name = (name or "").strip()
        if not name:
            raise ValidationError(_("Sub-Serial name is required."))

        lot_id = self.env.context.get("default_lot_id")
        if not lot_id:
            raise ValidationError(_("Select a Lot before creating a Sub-Serial."))

        lot = self.env["stock.lot"].browse(lot_id).exists()
        if not lot:
            raise ValidationError(_("The selected Lot no longer exists."))

        existing = self.search([("lot_id", "=", lot.id), ("name", "=", name)], limit=1)
        if existing:
            return existing.name_get()[0]

        subserial = self.create(
            {
                "name": name,
                "lot_id": lot.id,
            }
        )
        return subserial.name_get()[0]
