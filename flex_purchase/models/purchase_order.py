# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def sh_import_pol(self):
        """Compatibility hook for legacy import button kept in old inherited views."""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Import Purchase Order Lines'),
                'message': _('Legacy import feature is not installed in this environment.'),
                'type': 'warning',
                'sticky': False,
            },
        }


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_barcode = fields.Char(string='Barcode', related='product_id.barcode')
