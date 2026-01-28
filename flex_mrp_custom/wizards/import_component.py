# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from odoo.tools import ustr
import tempfile
import binascii

import csv
import base64
import logging

_logger = logging.getLogger(__name__)

try:
    import xlrd
except ImportError:
    _logger.debug('Importing xlrd failed')


class ImportComponent(models.TransientModel):
    _name = 'import.component'
    _description = 'Import Component'

    file = fields.Binary('File (xlsx)')
    filename = fields.Char('File Name')
    ignore_first_row = fields.Boolean('Ignore First Row')
    import_products_by = fields.Selection(
        [('default_code', 'Internal Reference'), ('name', 'Product Name')],
        string="Import Products By", required=True, default="default_code")
    import_method = fields.Selection(
        [('append', 'Append To Components'), ('replace', 'Replace Existing Components')],
        string="Import Method", required=True, default="append")
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order', required=True, readonly=True)
    line_ids = fields.One2many('import.component.line', 'wizard_id', string='Components')
    warning_btn = fields.Boolean(compute='_get_warning_btn')

    @api.depends('line_ids.product_id')
    def _get_warning_btn(self):
        for wiz in self:
            wiz.warning_btn = False
            if any([not line.product_id for line in wiz.line_ids]):
                wiz.warning_btn = True

    def warning_message(self, title=_("Warning"), body=_('Something went wrong!')):
        return {'warning': {'title': title, 'message': body, }}

    @api.onchange('file', 'ignore_first_row', 'import_products_by')
    def onchange_file(self):
        self.line_ids = [(5, 0, 0)]
        if not self.file:
            return False
        elif not self.filename.endswith('.xlsx'):
            self.file = ''
            self.filename = ''
            return self.warning_message(body=_("Only xlsx files are allowed!"))
        else:
            self._read_file()

    def _read_file(self):
        if not self.file:
            return False
        workbook = xlrd.open_workbook(file_contents=base64.decodebytes(self.file))
        if len(workbook.sheets()) > 0:
            sheet = workbook.sheets()[0]
            start_row = 0
            import_products_by = self.import_products_by
            if self.ignore_first_row:
                start_row = 1
            data = []
            get_cell_val = lambda cell: isinstance(cell.value, bytes) and cell.value.encode('utf-8') or str(cell.value)
            product_not_found = []
            qty_not_valid = []
            for row_no in range(start_row, sheet.nrows):
                row_values = list(map(get_cell_val, sheet.row(row_no)))

                print(f"row_values: {row_values}")

                # vals = [sheet.cell(row_no, col).value for col in range(2)]
                # print(f"vals: {vals}")
                product = self.env['product.product'].search([(import_products_by, '=', row_values[0])], limit=1)
                if not product:
                    product_not_found.append({'product': row_values[0], 'line': row_no + 1})
                try:
                    qty = float(row_values[1])
                except ValueError:
                    qty = 0.0
                    qty_not_valid.append({'qty': row_values[1], 'line': row_no + 1})
                data.append((0, 0, {
                    'product_id': product.id or False,
                    'qty': qty or 0.0,
                }))
            print(f"product_not_found: {product_not_found}")
            print(f"qty_not_valid: {qty_not_valid}")
            try:
                self.line_ids = data
            except Exception as ex:
                return self.warning_message(body=ex)
                # raise ValidationError(ex)
        else:
            return self.warning_message(body=_("No sheet found in the selected file!"))
            # raise ValidationError(_('No sheet found in the selected file.'))

    def action_import(self):
        # context = dict(self._context)
        # if context.get('default_production_id', False):
        #     context.pop('default_production_id')
        # self = self.with_context(context)
        if self.import_method == 'replace':
            self.production_id.move_raw_ids.unlink()
        lines = [{
            'product_id': line.product_id.id,
            'product_uom_qty': line.qty,
            'product_uom': line.product_uom.id,
            'name': line.product_id.partner_ref,
            'state': 'draft',
            'date': self.production_id.date_planned_start,
            'date_deadline': self.production_id.date_deadline,
            'location_id': self.production_id.location_src_id.id,
            'location_dest_id': self.production_id.production_location_id.id,
            'raw_material_production_id': self.production_id.id,
            'group_id' : self.production_id.procurement_group_id.id,
            'picking_type_id': self.production_id.picking_type_id.id,
            'company_id': self.production_id.company_id.id,
        } for line in self.line_ids if line.product_id]
        # self.env['stock.move'].create(lines)
        move_ids = self.production_id.move_raw_ids.with_context(default_production_id=False).create(lines)
        # move_ids = self.production_id.move_raw_ids.create(lines)
        for move in move_ids:
            move._onchange_product_id()
            move._onchange_product_uom_qty()

        self.production_id._onchange_move_raw()
        self.production_id._onchange_move_finished()
        self.production_id._onchange_workorder_ids()
        self.production_id._compute_components_availability()




class SaleGetProductLine(models.TransientModel):
    _name = 'import.component.line'
    _description = 'Import Component Line'

    wizard_id = fields.Many2one('import.component', string='Wizard')
    product_id = fields.Many2one('product.product', string='Product')
    product_uom = fields.Many2one('uom.uom', "UoM", related='product_id.uom_id')
    qty = fields.Float(string='Quantity')

    # @api.constrains('qty')
    # def check_qty(self):
    #     if self.filtered(lambda l: not l.qty > 0):
    #         raise ValidationError('Quantity must be positive.')
