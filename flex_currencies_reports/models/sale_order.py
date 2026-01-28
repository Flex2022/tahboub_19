# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import file_open, formatLang
import json


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    def get_iqd_currency(self):
        return self.env.company.currency_id.id

    additional_currency = fields.Many2one('res.currency', string='Report Currency', default=get_iqd_currency)
    additional_currency_rate = fields.Float(string='Currency Rate', default=1.0, required=True, digits=(12, 12),
                                            compute='compute_additional_currency_rate',
                                            store=True)
    additional_currency_rate_access = fields.Boolean(compute="compute_additional_currency_rate_access")
    # tax_totals_json_iqd = fields.Char(compute='_compute_tax_totals_json_iqd')

    tax_totals_iqd = fields.Binary(compute='_compute_tax_totals_iqd')
    tax_totals_json_egp = fields.Char(compute='_compute_tax_totals_json_egp')




    from odoo.tools import formatLang

    import json
    from odoo.tools import formatLang

    # def _compute_tax_totals_json_egp(self):
    #     for order in self:
    #         # Filter the order lines to include only those that are not of display type
    #         order_lines = order.order_line.filtered(lambda x: not x.display_type)
    #
    #         # Initialize the tax totals dictionary
    #         tax_totals = {
    #             'amount_untaxed': 0.0,
    #             'amount_total': 0.0,
    #             'subtotals': [],
    #             'groups_by_subtotal': {},
    #         }
    #
    #         # Compute taxes for each line
    #         for line in order_lines:
    #             # Compute the taxes for the line using the tax_id
    #             taxes = line.tax_id.compute_all(
    #                 price_unit=line.price_unit,
    #                 quantity=line.product_uom_qty,
    #                 currency=order.currency_id,
    #                 product=line.product_id
    #             )
    #             # Aggregate the untaxed and total amounts
    #             tax_totals['amount_untaxed'] += taxes['total_excluded']
    #             tax_totals['amount_total'] += taxes['total_included']
    #
    #             # Process the taxes by tax group
    #             for tax in taxes['taxes']:
    #                 group = tax['id']
    #                 # group = tax['tax_group_id']
    #                 # Add the tax group data to the 'groups_by_subtotal' dictionary
    #                 group_entry = tax_totals['groups_by_subtotal'].setdefault(group, {
    #                     'tax_group_amount': 0.0,
    #                     'tax_group_base_amount': 0.0,
    #                 })
    #                 group_entry['tax_group_amount'] += tax['amount']
    #                 group_entry['tax_group_base_amount'] += taxes['total_excluded']
    #
    #         # Convert amounts to the additional currency (EGP in this case)
    #         conversion_rate = order.additional_currency_rate
    #         tax_totals['amount_untaxed'] *= conversion_rate
    #         tax_totals['amount_total'] *= conversion_rate
    #
    #         # Format the amounts for display using the additional currency
    #         tax_totals['formatted_amount_untaxed'] = formatLang(
    #             self.env, tax_totals['amount_untaxed'], currency_obj=order.additional_currency
    #         )
    #         tax_totals['formatted_amount_total'] = formatLang(
    #             self.env, tax_totals['amount_total'], currency_obj=order.additional_currency
    #         )
    #
    #         # Format the tax group amounts in the groups_by_subtotal
    #         for group_key, group_values in tax_totals['groups_by_subtotal'].items():
    #             group_values['tax_group_amount'] *= conversion_rate
    #             group_values['tax_group_base_amount'] *= conversion_rate
    #             group_values['formatted_tax_group_amount'] = formatLang(
    #                 self.env, group_values['tax_group_amount'], currency_obj=order.additional_currency
    #             )
    #             group_values['formatted_tax_group_base_amount'] = formatLang(
    #                 self.env, group_values['tax_group_base_amount'], currency_obj=order.additional_currency
    #             )
    #
    #         # Serialize the tax totals dictionary to JSON and store it in the order record
    #         order.tax_totals_json_egp = json.dumps(tax_totals)

    def compute_additional_currency_rate_access(self):
        for move in self:
            move.additional_currency_rate_access = self.env.user.has_group(
                'flex_currencies_reports.group_display_currency_rate')

    # Get the currency rates between two currencies
    def get_currency_rate(self, order, from_currency_id, to_currency_id):
        currency_obj = self.env['res.currency']
        rate = currency_obj._get_conversion_rate(from_currency_id, to_currency_id, order.company_id,
                                                 fields.Date.today())
        return rate

    @api.depends('currency_id', 'additional_currency')
    def compute_additional_currency_rate(self):
        for order in self:
            order.additional_currency_rate = 1.0
            if order.currency_id and order.additional_currency:
                order.additional_currency_rate = self.get_currency_rate(order, order.currency_id,
                                                                        order.additional_currency)

    @api.depends('order_line.tax_ids', 'order_line.price_unit', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json_egp(self):
        def compute_taxes(order_line):
            price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
            order = order_line.order_id
            return order_line.tax_ids._origin.compute_all(price, order.currency_id, order_line.product_uom_qty,
                                                         product=order_line.product_id,
                                                         partner=order.partner_shipping_id)

        account_move = self.env['account.move']
        for order in self:
            tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line,
                                                                                         compute_taxes)
            tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total,
                                                      order.amount_untaxed, order.currency_id)

            # Adding this lines to change the amount currency
            tax_totals['amount_total'] = tax_totals['amount_total'] * order.additional_currency_rate
            tax_totals['formatted_amount_total'] = formatLang(self.env, tax_totals['amount_total'],
                                                              currency_obj=order.additional_currency)
            tax_totals['amount_untaxed'] = tax_totals['amount_untaxed'] * order.additional_currency_rate
            tax_totals['formatted_amount_untaxed'] = formatLang(self.env, tax_totals['amount_untaxed'],
                                                                currency_obj=order.additional_currency)
            # Change Untaxed Amount
            if tax_totals['groups_by_subtotal'].get('Untaxed Amount'):
                untaxed_amounts = []
                for group in tax_totals['groups_by_subtotal']['Untaxed Amount']:
                    group['tax_group_amount'] = group['tax_group_amount'] * order.additional_currency_rate
                    group['formatted_tax_group_amount'] = formatLang(self.env, group['tax_group_amount'],
                                                                     currency_obj=order.additional_currency)
                    group['tax_group_base_amount'] = group['tax_group_base_amount'] * order.additional_currency_rate
                    group['formatted_tax_group_base_amount'] = formatLang(self.env, group['tax_group_base_amount'],
                                                                          currency_obj=order.additional_currency)

                    untaxed_amounts.append(group)

                # Change Group with IQD Group
                tax_totals['groups_by_subtotal']['Untaxed Amount'] = untaxed_amounts

            # Change subtotals
            if tax_totals['subtotals']:
                for subtotal in tax_totals['subtotals']:
                    subtotal['amount'] = subtotal['amount'] * order.additional_currency_rate
                    subtotal['formatted_amount'] = formatLang(self.env, subtotal['amount'],
                                                              currency_obj=order.additional_currency)

            order.tax_totals_json_egp = json.dumps(tax_totals)

    def _compute_tax_totals_iqd(self):
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            order.tax_totals_iqd = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.additional_currency,
            )
            # convert it to iqd
            order.tax_totals_iqd['amount_untaxed'] = order.tax_totals_iqd[
                                                        'amount_untaxed'] * order.additional_currency_rate
            order.tax_totals_iqd['amount_total'] = order.tax_totals_iqd[
                                                      'amount_total'] * order.additional_currency_rate

            order.tax_totals_iqd['formatted_amount_untaxed'] = formatLang(self.env,
                                                                         order.tax_totals_iqd['amount_untaxed'],
                                                                         currency_obj=order.additional_currency)
            order.tax_totals_iqd['formatted_amount_total'] = formatLang(self.env,
                                                                       order.tax_totals_iqd['amount_total'],
                                                                       currency_obj=order.additional_currency)

            # Change Group with IQD Group

            if order.tax_totals_iqd['subtotals']:
                untaxed_amounts = []
                for group in order.tax_totals_iqd['subtotals']:
                    group['amount'] = group['amount'] * order.additional_currency_rate
                    group['formatted_amount'] = formatLang(self.env, group['amount'],
                                                           currency_obj=order.additional_currency)
                    untaxed_amounts.append(group)
                # Change Group with IQD Group
                order.tax_totals_iqd['subtotals'] = untaxed_amounts

            # Change currency and rate of groups
            if order.tax_totals_iqd['groups_by_subtotal'].get('Untaxed Amount'):
                untaxed_amounts = []
                for group in order.tax_totals_iqd['groups_by_subtotal']['Untaxed Amount']:
                    group['tax_group_amount'] = group['tax_group_amount'] * order.additional_currency_rate
                    group['formatted_tax_group_amount'] = formatLang(self.env, group['tax_group_amount'],
                                                                     currency_obj=order.additional_currency)
                    group['tax_group_base_amount'] = group['tax_group_base_amount'] * order.additional_currency_rate
                    group['formatted_tax_group_base_amount'] = formatLang(self.env, group['tax_group_base_amount'],
                                                                          currency_obj=order.additional_currency)

                    untaxed_amounts.append(group)

                # Change Group with IQD Group
                order.tax_totals_iqd['groups_by_subtotal']['Untaxed Amount'] = untaxed_amounts

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if self.currency_id.id != self.additional_currency.id:
            if self.additional_currency_rate_access:
                if self.additional_currency_rate != self.get_currency_rate(self, self.currency_id,
                                                                           self.additional_currency):
                    self.create_new_currency_rate()
        return res

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if self.currency_id.id != self.additional_currency.id:
            if self.additional_currency_rate_access:
                if self.additional_currency_rate != self.get_currency_rate(self, self.currency_id,
                                                                           self.additional_currency):
                    self.create_new_currency_rate()
        return res

    def create_new_currency_rate(self):
        currency_rate = self.env['res.currency.rate'].search(
            [('name', '=', fields.Date.today()), ('currency_id', '=', self.currency_id.id),
             ('company_id', '=', self.company_id.id)])
        if currency_rate:
            currency_rate.write({'inverse_company_rate': self.additional_currency_rate})
        else:
            self.env['res.currency.rate'].sudo().create({
                'name': fields.Date.today(),
                'inverse_company_rate': self.additional_currency_rate,
                'currency_id': self.currency_id.id,
                'company_id': self.company_id.id
            })

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'currency_id': self.currency_id.id,
            'additional_currency': self.additional_currency.id,
            'additional_currency_rate': self.additional_currency_rate,
        })
        return invoice_vals

    # def _create_invoices(self, grouped=False, final=False, date=None):
    #     res = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)
    #     # send currency_id
    #     for move in res:
    #         move.write({'currency_id': self.currency_id.id, 'additional_currency': self.additional_currency.id})
    #         move.write({'additional_currency_rate': self.additional_currency_rate})
    #     return res


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    additional_currency = fields.Many2one('res.currency', related='order_id.additional_currency')
    price_unit_iqd = fields.Float('Price unit (IQD)', compute='compute_price_unit_iqd')
    price_subtotal_iqd = fields.Float('Price Subtotal (IQD)', compute='compute_price_unit_iqd')
    price_total_iqd = fields.Float('Price Total (IQD)', compute='compute_price_unit_iqd')
    price_subtotal_egp = fields.Float('Price Subtotal (EGP)', compute='compute_price_unit_egp')
    price_tax_egp = fields.Float('Price Tax (EGP)', compute='compute_price_unit_egp')

    # Use @api.depends to ensure they recompute when values change
    @api.depends('price_subtotal', 'price_tax', 'order_id.additional_currency_rate')
    def compute_price_unit_egp(self):
        for line in self:
            # Get the rate, default to 1.0 if not set to avoid multiplication by zero
            rate = line.order_id.additional_currency_rate or 1.0

            # Use the rate if an additional currency exists, otherwise 1.0
            if line.additional_currency:
                line.price_subtotal_egp = line.price_subtotal * rate
                line.price_tax_egp = line.price_tax * rate
            else:
                line.price_subtotal_egp = line.price_subtotal
                line.price_tax_egp = line.price_tax

    @api.depends('price_unit', 'price_subtotal', 'price_total', 'order_id.additional_currency_rate')
    def compute_price_unit_iqd(self):
        for line in self:
            rate = line.order_id.additional_currency_rate or 1.0

            if line.additional_currency:
                line.price_unit_iqd = line.price_unit * rate
                line.price_subtotal_iqd = line.price_subtotal * rate
                line.price_total_iqd = line.price_total * rate
            else:
                line.price_unit_iqd = line.price_unit
                line.price_subtotal_iqd = line.price_subtotal
                line.price_total_iqd = line.price_total


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        # send currency_id
        res.write({'currency_id': order.currency_id.id})
        return res
