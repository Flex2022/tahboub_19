# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

import base64
import logging

_logger = logging.getLogger(__name__)

try:
    import xlrd
except ImportError:
    xlrd = None
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
            wiz.warning_btn = any(not line.product_id for line in wiz.line_ids)

    def warning_message(self, title=None, body=None):
        title = title or _("Warning")
        body = body or _('Something went wrong!')
        return {'warning': {'title': title, 'message': body}}

    @api.onchange('file', 'ignore_first_row', 'import_products_by')
    def onchange_file(self):
        self.line_ids = [(5, 0, 0)]
        if not self.file:
            return False
        if not (self.filename or '').lower().endswith('.xlsx'):
            self.file = False
            self.filename = False
            return self.warning_message(body=_("Only xlsx files are allowed!"))
        return self._read_file()

    def _read_file(self):
        if not self.file:
            return False
        if xlrd is None:
            return self.warning_message(body=_("Python library 'xlrd' is required to read xlsx files."))

        try:
            workbook = xlrd.open_workbook(file_contents=base64.b64decode(self.file))
        except Exception as exc:
            _logger.exception("Failed to read component import file")
            return self.warning_message(body=str(exc))

        sheets = workbook.sheets()
        if not sheets:
            return self.warning_message(body=_("No sheet found in the selected file!"))

        sheet = sheets[0]
        start_row = 1 if self.ignore_first_row else 0
        search_field = self.import_products_by or 'default_code'

        data = []
        product_not_found = []
        qty_not_valid = []

        def _cell_to_text(cell):
            value = cell.value
            if isinstance(value, bytes):
                return value.decode('utf-8', errors='ignore').strip()
            return str(value).strip()

        for row_no in range(start_row, sheet.nrows):
            row = sheet.row(row_no)
            if not row:
                continue

            code_or_name = _cell_to_text(row[0]) if len(row) >= 1 else ''
            qty_text = _cell_to_text(row[1]) if len(row) >= 2 else ''
            if not code_or_name and not qty_text:
                continue

            product = self.env['product.product'].search([(search_field, '=', code_or_name)], limit=1)
            if not product:
                product_not_found.append({'product': code_or_name, 'line': row_no + 1})

            try:
                qty = float(qty_text)
            except (TypeError, ValueError):
                qty = 0.0
                qty_not_valid.append({'qty': qty_text, 'line': row_no + 1})

            data.append((0, 0, {
                'product_id': product.id or False,
                'qty': qty,
            }))

        self.line_ids = data

        if product_not_found or qty_not_valid:
            details = []
            if product_not_found:
                details.append(_("Products not found: %s") % ', '.join(str(x['line']) for x in product_not_found[:10]))
            if qty_not_valid:
                details.append(_("Invalid quantity: %s") % ', '.join(str(x['line']) for x in qty_not_valid[:10]))
            return self.warning_message(body=' | '.join(details))
        return False

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
            'name': line.product_id.partner_ref or line.product_id.display_name,
            'state': 'draft',
            'date': self.production_id.date_planned_start,
            'date_deadline': self.production_id.date_deadline,
            'location_id': self.production_id.location_src_id.id,
            'location_dest_id': self.production_id.production_location_id.id,
            'raw_material_production_id': self.production_id.id,
            'group_id': self.production_id.procurement_group_id.id,
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
