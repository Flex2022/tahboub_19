# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


# =========================================================
# Wizard: Sale Advance Payment Invoice
# =========================================================
class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    select_order_line_to_invoice = fields.Boolean(
        string="Select Order Lines To Invoice"
    )
    order_line_ids = fields.Many2many(
        'sale.order.line',
        string="Order Lines"
    )

    # -----------------------------------------------------
    # ONCHANGE
    # -----------------------------------------------------
    @api.onchange('select_order_line_to_invoice')
    def _onchange_select_order_line_to_invoice(self):
        if not self.sale_order_ids or len(self.sale_order_ids) != 1:
            self.order_line_ids = False
            return

        if not self.select_order_line_to_invoice:
            self.order_line_ids = False
            return {
                'domain': {
                    'order_line_ids': [('id', '=', False)]
                }
            }

        order = self.sale_order_ids
        return {
            'domain': {
                'order_line_ids': [
                    ('order_id', '=', order.id),
                    ('display_type', '=', False),
                ]
            }
        }

    # -----------------------------------------------------
    # ACTION
    # -----------------------------------------------------
    def create_invoices(self):
        self._check_amount_is_positive()

        # Store selected lines on sale order (only for delivered invoices)
        if (
            self.advance_payment_method == 'delivered'
            and self.select_order_line_to_invoice
            and self.sale_order_ids
        ):
            if not self.order_line_ids:
                raise UserError(_("Please select at least one order line to invoice."))

            self.sale_order_ids.write({
                'select_order_line_to_invoice': True,
                'selected_order_line_ids': [(6, 0, self.order_line_ids.ids)],
            })

        invoices = self._create_invoices(self.sale_order_ids)
        return self.sale_order_ids.action_view_invoice(invoices=invoices)


# =========================================================
# Sale Order Extension
# =========================================================
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    select_order_line_to_invoice = fields.Boolean()
    selected_order_line_ids = fields.Many2many('sale.order.line')

    # -----------------------------------------------------
    # Override: Invoiceable lines logic
    # -----------------------------------------------------
    def _get_invoiceable_lines(self, final=False):
        self.ensure_one()

        # Default behavior
        if not self.select_order_line_to_invoice:
            return super()._get_invoiceable_lines(final)

        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure'
        )

        invoiceable_lines = self.env['sale.order.line']
        pending_section = None
        down_payment_lines = self.env['sale.order.line']

        for line in self.selected_order_line_ids:
            if line.display_type == 'line_section':
                pending_section = line
                continue

            if (
                line.display_type != 'line_note'
                and float_is_zero(line.qty_to_invoice, precision_digits=precision)
            ):
                continue

            if line.is_downpayment:
                down_payment_lines |= line
                continue

            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
                if pending_section:
                    invoiceable_lines |= pending_section
                    pending_section = None
                invoiceable_lines |= line

        # Down payment lines must always be added at the end
        return invoiceable_lines | down_payment_lines










# class SaleAdvancePaymentInv(models.TransientModel):
#     _inherit = "sale.advance.payment.inv"
#
#
#     select_order_line_to_invoice = fields.Boolean('Select Order Line To Invoice')
#     order_line = fields.Many2many('sale.order.line', string='Order Line')
#
#
#     @api.onchange('order_line')
#     def _onchange_order_line(self):
#         sale_order_id = self.env['sale.order'].browse(self.env.context.get('active_id'))
#         sale_order_id.ab_order_line_from_create = self.order_line
#         return {'domain': {
#             'order_line': [('order_id', '=', sale_order_id.id)]}}
#
#     @api.onchange('select_order_line_to_invoice')
#     def _onchange_select_order_line_to_invoice(self):
#         sale_order_id = self.env['sale.order'].browse(self.env.context.get('active_id'))
#         sale_order_id.select_order_line_to_invoice = self.select_order_line_to_invoice
#
#
#     def create_invoices(self):
#         sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
#
#         if self.advance_payment_method == 'delivered':
#             sale_orders._create_invoices(final=self.deduct_down_payments)
#         else:
#             # Create deposit product if necessary
#             if not self.product_id:
#                 vals = self._prepare_deposit_product()
#                 self.product_id = self.env['product.product'].create(vals)
#                 self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)
#
#             sale_line_obj = self.env['sale.order.line']
#             for order in sale_orders:
#                 amount, name = self._get_advance_details(order)
#
#                 if self.product_id.invoice_policy != 'order':
#                     raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
#                 if self.product_id.type != 'service':
#                     raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
#                 taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
#                 tax_ids = order.fiscal_position_id.map_tax(taxes).ids
#                 analytic_tag_ids = []
#                 for line in order.order_line:
#                     analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
#
#                 so_line_values = self._prepare_so_line(order, analytic_tag_ids, tax_ids, amount)
#                 so_line = sale_line_obj.create(so_line_values)
#                 self._create_invoice(order, so_line, amount)
#         if self._context.get('open_invoices', False):
#             return sale_orders.action_view_invoice()
#         return {'type': 'ir.actions.act_window_close'}
#
#
# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     ab_order_line_from_create = fields.Many2many('sale.order.line')
#     select_order_line_to_invoice = fields.Boolean()
#
#     def _create_invoices(self, grouped=False, final=False, date=None):
#         """
#         Create the invoice associated to the SO.
#         :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
#                         (partner_invoice_id, currency)
#         :param final: if True, refunds will be generated if necessary
#         :returns: list of created invoices
#         """
#         if not self.env['account.move'].check_access_rights('create', False):
#             try:
#                 self.check_access_rights('write')
#                 self.check_access_rule('write')
#             except AccessError:
#                 return self.env['account.move']
#
#         # 1) Create invoices.
#         invoice_vals_list = []
#         invoice_item_sequence = 0 # Incremental sequencing to keep the lines order on the invoice.
#         for order in self:
#             order = order.with_company(order.company_id)
#             current_section_vals = None
#             down_payments = order.env['sale.order.line']
#
#             invoice_vals = order._prepare_invoice()
#             invoiceable_lines = order._get_invoiceable_lines(final)
#
#             if not any(not line.display_type for line in invoiceable_lines):
#                 continue
#
#             invoice_line_vals = []
#             down_payment_section_added = False
#             for line in invoiceable_lines:
#                 if not down_payment_section_added and line.is_downpayment:
#                     # Create a dedicated section for the down payments
#                     # (put at the end of the invoiceable_lines)
#                     invoice_line_vals.append(
#                         (0, 0, order._prepare_down_payment_section_line(
#                             sequence=invoice_item_sequence,
#                         )),
#                     )
#                     down_payment_section_added = True
#                     invoice_item_sequence += 1
#                 invoice_line_vals.append(
#                     (0, 0, line._prepare_invoice_line(
#                         sequence=invoice_item_sequence,
#                     )),
#                 )
#                 invoice_item_sequence += 1
#
#             invoice_vals['invoice_line_ids'] += invoice_line_vals
#             invoice_vals_list.append(invoice_vals)
#
#         if not invoice_vals_list:
#             raise self._nothing_to_invoice_error()
#
#         # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
#         if not grouped:
#             new_invoice_vals_list = []
#             invoice_grouping_keys = self._get_invoice_grouping_keys()
#             invoice_vals_list = sorted(
#                 invoice_vals_list,
#                 key=lambda x: [
#                     x.get(grouping_key) for grouping_key in invoice_grouping_keys
#                 ]
#             )
#             for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
#                 origins = set()
#                 payment_refs = set()
#                 refs = set()
#                 ref_invoice_vals = None
#                 for invoice_vals in invoices:
#                     if not ref_invoice_vals:
#                         ref_invoice_vals = invoice_vals
#                     else:
#                         ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
#                     origins.add(invoice_vals['invoice_origin'])
#                     payment_refs.add(invoice_vals['payment_reference'])
#                     refs.add(invoice_vals['ref'])
#                 ref_invoice_vals.update({
#                     'ref': ', '.join(refs)[:2000],
#                     'invoice_origin': ', '.join(origins),
#                     'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
#                 })
#                 new_invoice_vals_list.append(ref_invoice_vals)
#             invoice_vals_list = new_invoice_vals_list
#
#         # 3) Create invoices.
#
#         # As part of the invoice creation, we make sure the sequence of multiple SO do not interfere
#         # in a single invoice. Example:
#         # SO 1:
#         # - Section A (sequence: 10)
#         # - Product A (sequence: 11)
#         # SO 2:
#         # - Section B (sequence: 10)
#         # - Product B (sequence: 11)
#         #
#         # If SO 1 & 2 are grouped in the same invoice, the result will be:
#         # - Section A (sequence: 10)
#         # - Section B (sequence: 10)
#         # - Product A (sequence: 11)
#         # - Product B (sequence: 11)
#         #
#         # Resequencing should be safe, however we resequence only if there are less invoices than
#         # orders, meaning a grouping might have been done. This could also mean that only a part
#         # of the selected SO are invoiceable, but resequencing in this case shouldn't be an issue.
#         if len(invoice_vals_list) < len(self):
#             SaleOrderLine = self.env['sale.order.line']
#             for invoice in invoice_vals_list:
#                 sequence = 1
#                 for line in invoice['invoice_line_ids']:
#                     line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
#                     sequence += 1
#
#         # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
#         # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
#         moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)
#
#         # 4) Some moves might actually be refunds: convert them if the total amount is negative
#         # We do this after the moves have been created since we need taxes, etc. to know if the total
#         # is actually negative or not
#         if final:
#             moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
#         for move in moves:
#             move.message_post_with_view('mail.message_origin_link',
#                 values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
#                 subtype_id=self.env.ref('mail.mt_note').id
#             )
#         return moves
#
#
#     def _get_invoiceable_lines(self, final=False):
#         """Return the invoiceable lines for order `self`."""
#         down_payment_line_ids = []
#         invoiceable_line_ids = []
#         pending_section = None
#         precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
#         if self.select_order_line_to_invoice:
#             for line in self.ab_order_line_from_create:
#                 if line.display_type == 'line_section':
#                     # Only invoice the section if one of its lines is invoiceable
#                     pending_section = line
#                     continue
#                 if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
#                     continue
#                 if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
#                     if line.is_downpayment:
#                         # Keep down payment lines separately, to put them together
#                         # at the end of the invoice, in a specific dedicated section.
#                         down_payment_line_ids.append(line.id)
#                         continue
#                     if pending_section:
#                         invoiceable_line_ids.append(pending_section.id)
#                         pending_section = None
#                     invoiceable_line_ids.append(line.id)
#             picking_id = self.picking_ids.filtered(lambda p: p.state != 'cancel')
#             if picking_id.state != 'draft':
#                 picking_id.picking_draft_from_code(picking_id)
#             sale_order_line_to_create = self.ab_order_line_from_create
#             product_ids = sale_order_line_to_create.mapped('product_id').ids
#             picking_line = picking_id.move_ids
#             picking_line_filtered = picking_line.filtered(lambda p: p.product_id.id in product_ids)
#             print(picking_line_filtered)
#             self.env['split.transfer.confirm'].split_from_code(picking_line_filtered.ids)
#             picking_ids = self.picking_ids.filtered(lambda p: p.state != 'cancel')
#             for picking_id in picking_ids:
#                 picking_id.action_confirm()
#         else:
#             for line in self.order_line:
#                 if line.display_type == 'line_section':
#                     # Only invoice the section if one of its lines is invoiceable
#                     pending_section = line
#                     continue
#                 if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
#                     continue
#                 if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
#                     if line.is_downpayment:
#                         # Keep down payment lines separately, to put them together
#                         # at the end of the invoice, in a specific dedicated section.
#                         down_payment_line_ids.append(line.id)
#                         continue
#                     if pending_section:
#                         invoiceable_line_ids.append(pending_section.id)
#                         pending_section = None
#                     invoiceable_line_ids.append(line.id)
#
#
#         return self.env['sale.order.line'].browse(invoiceable_line_ids + down_payment_line_ids)
#
