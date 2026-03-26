# -*- coding: utf-8 -*-
from odoo import fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    # Legacy custom views may still use this symbol in invisible expressions.
    show_copy_operations_button = fields.Boolean(default=False)

    # Compatibility shim for broken/stale views using old method names.
    def action_copy_existing_operations(self):
        self.ensure_one()
        return self.action_open_operation_form()

    # Some views call this name directly on mrp.bom by mistake.
    def copy_existing_operations(self):
        return self.action_copy_existing_operations()

