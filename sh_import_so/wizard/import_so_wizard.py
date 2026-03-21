from odoo import _, fields, models


class ImportSOWizard(models.TransientModel):
    _name = "import.so.wizard"
    _description = "Import Sale Order Wizard"

    import_type = fields.Selection(
        [("csv", "CSV File"), ("excel", "Excel File")],
        default="csv",
        string="Import File Type",
        required=True,
    )
    file = fields.Binary(string="File", required=True)
    product_by = fields.Selection(
        [("name", "Name"), ("int_ref", "Internal Reference"), ("barcode", "Barcode")],
        default="name",
        string="Product By",
        required=True,
    )
    is_create_customer = fields.Boolean(string="Create Customer?")
    is_confirm_sale = fields.Boolean(string="Auto Confirm Sale?")
    order_no_type = fields.Selection(
        [("auto", "Auto"), ("as_per_sheet", "As per sheet")],
        default="auto",
        string="Quotation/Order Number",
        required=True,
    )

    def import_so_apply(self):
        self.ensure_one()
        if not self.file:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Import Sale Order"),
                    "message": _("Please upload a file first."),
                    "type": "warning",
                    "sticky": False,
                },
            }
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Import Sale Order"),
                "message": _("Wizard is now loaded correctly. Full importer migration can be done next."),
                "type": "success",
                "sticky": False,
            },
        }

