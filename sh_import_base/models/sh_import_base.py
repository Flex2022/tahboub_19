# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from email.policy import default
from odoo import fields, models, _
from odoo.exceptions import UserError


class ImportBase(models.Model):
    _name = "sh.import.base"
    _description = "The Base Module For all Imports"

    name = fields.Char("Name")
    sh_technical_name = fields.Char("Technical Name")
    sh_image_name = fields.Char("Image Name")
    import_limit = fields.Integer("Import Limit", default=0)
    on_error = fields.Selection(
        [('continue', 'Continue'), ('breal', 'Break')], default="continue", string="On Error")
    sh_import_product_img_boolean = fields.Boolean("Legacy Product Image Import")
    sh_import_supplier_info_boolean = fields.Boolean("Legacy Supplier Import")
    import_type = fields.Selection([('csv', 'CSV File'), ('excel', 'Excel File')], default='csv')
    product_by = fields.Selection([
        ('name', 'Name'),
        ('int_ref', 'Internal Reference'),
        ('barcode', 'Barcode'),
    ], default='name')
    product_model = fields.Selection([
        ('product_template', 'Product Template'),
        ('product_product', 'Product Variant'),
    ], default='product_product')
    sh_import_type_supplier = fields.Selection([('csv', 'CSV File'), ('excel', 'Excel File')], default='csv')
    sh_method_supplier = fields.Selection([('create', 'Create'), ('update', 'Update')], default='create')
    sh_product_by_supplier = fields.Selection([
        ('name', 'Name'),
        ('int_ref', 'Internal Reference'),
        ('barcode', 'Barcode'),
    ], default='name')
    sh_product_model_supplier = fields.Selection([
        ('product_template', 'Product Template'),
        ('product_product', 'Product Variant'),
    ], default='product_product')

    def create_store_record(self):
        view = self.env.ref('sh_import_base.sh_import_Store_form')
        return {
            'name': 'Import',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sh.import.store',
            'view_id': view.id,
            'target': 'new',
            'context': {
                'default_base_id': self.id
            }
        }

    def view_Store_done(self):
        tree_view = self.env.ref('sh_import_base.sh_import_store_tree')
        form_view = self.env.ref('sh_import_base.sh_import_Store_form')
        return {
            'name': 'Import',
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'res_model': 'sh.import.store',
            'views': [(tree_view.id, 'list'), (form_view.id, 'form')],
            'view_id': tree_view.id,
            'target': '_blank',
            'domain': [('base_id', '=', self.id), ('state', '=', 'done')]
        }

    def view_Store_error(self):
        tree_view = self.env.ref('sh_import_base.sh_import_store_tree')
        form_view = self.env.ref('sh_import_base.sh_import_Store_form')
        return {
            'name': 'Import',
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'res_model': 'sh.import.store',
            'views': [(tree_view.id, 'list'), (form_view.id, 'form')],
            'view_id': tree_view.id,
            'target': '_blank',
            'domain': [('base_id', '=', self.id), ('state', '=', 'error')]
        }

    def view_Store_running(self):
        tree_view = self.env.ref('sh_import_base.sh_import_store_tree')
        form_view = self.env.ref('sh_import_base.sh_import_Store_form')
        return {
            'name': 'Import',
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'res_model': 'sh.import.store',
            'views': [(tree_view.id, 'list'), (form_view.id, 'form')],
            'view_id': tree_view.id,
            'target': '_blank',
            'domain': [('base_id', '=', self.id), ('state', '=', 'running')]
        }

    def view_Store_all(self):
        tree_view = self.env.ref('sh_import_base.sh_import_store_tree')
        form_view = self.env.ref('sh_import_base.sh_import_Store_form')
        return {
            'name': 'Import',
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'res_model': 'sh.import.store',
            'views': [(tree_view.id, 'list'), (form_view.id, 'form')],
            'view_id': tree_view.id,
            'target': '_blank',
            'domain': [('base_id', '=', self.id)]
        }

    def add_default_value(self):
        view = self.env.ref('sh_import_base.sh_import_base_form')
        return {
            'name': 'Default Value',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sh.import.base',
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id
        }

    def _legacy_import_not_supported(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Legacy Import'),
                'message': _('This legacy import action is not supported in this migrated package.'),
                'type': 'warning',
                'sticky': False,
            },
        }

    def import_product_img_apply(self):
        return self._legacy_import_not_supported()

    def import_supplier_info_apply(self):
        return self._legacy_import_not_supported()
