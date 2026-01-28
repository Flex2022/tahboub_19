# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import file_open, formatLang
import json


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    def get_iqd_currency(self):
        return self.env.company.currency_id.id

    additional_currency = fields.Many2one('res.currency', string='Report Currency', default=get_iqd_currency)
    additional_currency_rate = fields.Float(string='Currency Rate', default=1.0, required=True, digits=(12, 12),
                                            compute='compute_additional_currency_rate',
                                            store=True)
    additional_currency_rate_access = fields.Boolean(compute="compute_additional_currency_rate_access")
    tax_totals_iqd = fields.Binary(compute='_compute_tax_totals_iqd')

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

    @api.depends('line_ids.amount_currency', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id',
                 'currency_id', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json_iqd(self):
        """ Computed field used for custom widget's rendering.
            Only set on invoices.
        """
        for move in self:
            if not move.is_invoice(include_receipts=True):
                # Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
                move.tax_totals_json_iqd = None
                continue

            tax_lines_data = move._prepare_tax_lines_data_for_totals_from_invoice()

            tax_totals_json_iqd = {
                **self._get_tax_totals(move.partner_id,
                                       tax_lines_data,
                                       move.amount_total * move.additional_currency_rate,
                                       move.amount_untaxed * move.additional_currency_rate,
                                       move.additional_currency),
                'allow_tax_edition': move.is_purchase_document(include_receipts=False) and move.state == 'draft',
            }

            # Change currency and rate of groups
            if tax_totals_json_iqd['groups_by_subtotal'].get('Untaxed Amount'):
                untaxed_amounts = []
                for group in tax_totals_json_iqd['groups_by_subtotal']['Untaxed Amount']:
                    group['tax_group_amount'] = group['tax_group_amount'] * move.additional_currency_rate
                    group['formatted_tax_group_amount'] = formatLang(self.env, group['tax_group_amount'],
                                                                     currency_obj=move.additional_currency)
                    group['tax_group_base_amount'] = group['tax_group_base_amount'] * move.additional_currency_rate
                    group['formatted_tax_group_base_amount'] = formatLang(self.env, group['tax_group_base_amount'],
                                                                          currency_obj=move.additional_currency)

                    untaxed_amounts.append(group)

                # Change Group with IQD Group
                tax_totals_json_iqd['groups_by_subtotal']['Untaxed Amount'] = untaxed_amounts

            # dumps the result
            move.tax_totals_json_iqd = json.dumps(tax_totals_json_iqd)

    def _compute_tax_totals_iqd(self):
        """ Computed field used for custom widget's rendering.
            Only set on invoices.
        """
        for move in self:
            if move.is_invoice(include_receipts=True):
                base_lines = move.invoice_line_ids.filtered(lambda line: line.display_type == 'product')
                base_line_values_list = [line._convert_to_tax_base_line_dict() for line in base_lines]
                sign = move.direction_sign
                if move.id:
                    # The invoice is stored so we can add the early payment discount lines directly to reduce the
                    # tax amount without touching the untaxed amount.
                    base_line_values_list += [
                        {
                            **line._convert_to_tax_base_line_dict(),
                            'handle_price_include': False,
                            'quantity': 1.0,
                            'price_unit': sign * line.amount_currency,

                        }
                        for line in move.line_ids.filtered(lambda line: line.display_type == 'epd')
                    ]

                kwargs = {
                    'base_lines': base_line_values_list,
                    'currency': move.additional_currency,
                }

                if move.id:
                    kwargs['tax_lines'] = [
                        line._convert_to_tax_line_dict()
                        for line in move.line_ids.filtered(lambda line: line.display_type == 'tax')
                    ]
                else:
                    # In case the invoice isn't yet stored, the early payment discount lines are not there. Then,
                    # we need to simulate them.
                    epd_aggregated_values = {}
                    for base_line in base_lines:
                        if not base_line.epd_needed:
                            continue
                        for grouping_dict, values in base_line.epd_needed.items():
                            epd_values = epd_aggregated_values.setdefault(grouping_dict, {'price_subtotal': 0.0})
                            epd_values['price_subtotal'] += values['price_subtotal']

                    for grouping_dict, values in epd_aggregated_values.items():
                        taxes = None
                        if grouping_dict.get('tax_ids'):
                            taxes = self.env['account.tax'].browse(grouping_dict['tax_ids'][0][2])

                        kwargs['base_lines'].append(self.env['account.tax']._convert_to_tax_base_line_dict(
                            None,
                            partner=move.partner_id,
                            currency=move.additional_currency,
                            taxes=taxes,
                            price_unit=values['price_subtotal'] * move.additional_currency_rate,
                            quantity=1.0,
                            account=self.env['account.account'].browse(grouping_dict['account_id']),
                            analytic_distribution=values.get('analytic_distribution'),
                            price_subtotal=values['price_subtotal'] * move.additional_currency_rate,
                            is_refund=move.move_type in ('out_refund', 'in_refund'),
                            handle_price_include=False,
                        ))
                move.tax_totals_iqd = self.env['account.tax']._prepare_tax_totals(**kwargs)

                # convert it to iqd
                move.tax_totals_iqd['amount_untaxed'] = move.tax_totals_iqd[
                                                            'amount_untaxed'] * move.additional_currency_rate
                move.tax_totals_iqd['amount_total'] = move.tax_totals_iqd[
                                                          'amount_total'] * move.additional_currency_rate

                move.tax_totals_iqd['formatted_amount_untaxed'] = formatLang(self.env,
                                                                             move.tax_totals_iqd['amount_untaxed'],
                                                                             currency_obj=move.additional_currency)
                move.tax_totals_iqd['formatted_amount_total'] = formatLang(self.env,
                                                                           move.tax_totals_iqd['amount_total'],
                                                                           currency_obj=move.additional_currency)

                rounding_line = move.line_ids.filtered(lambda l: l.display_type == 'rounding')
                if rounding_line:
                    amount_total_rounded = move.tax_totals[
                                               'amount_total'] * move.additional_currency_rate + sign * rounding_line.amount_currency
                    move.tax_totals_iqd['amount_total_rounded'] = amount_total_rounded
                    move.tax_totals_iqd['formatted_amount_total_rounded'] = formatLang(self.env, amount_total_rounded,
                                                                                       currency_obj=move.additional_currency) or ''
                # Change Group with IQD Group

                if move.tax_totals_iqd['subtotals']:
                    untaxed_amounts = []
                    for group in move.tax_totals_iqd['subtotals']:
                        group['amount'] = group['amount'] * move.additional_currency_rate
                        group['formatted_amount'] = formatLang(self.env, group['amount'],
                                                                         currency_obj=move.additional_currency)
                        untaxed_amounts.append(group)
                    # Change Group with IQD Group
                    move.tax_totals_iqd['subtotals'] = untaxed_amounts

                # Change currency and rate of groups
                if move.tax_totals_iqd['groups_by_subtotal'].get('Untaxed Amount'):
                    untaxed_amounts = []
                    for group in move.tax_totals_iqd['groups_by_subtotal']['Untaxed Amount']:
                        group['tax_group_amount'] = group['tax_group_amount'] * move.additional_currency_rate
                        group['formatted_tax_group_amount'] = formatLang(self.env, group['tax_group_amount'],
                                                                         currency_obj=move.additional_currency)
                        group['tax_group_base_amount'] = group['tax_group_base_amount'] * move.additional_currency_rate
                        group['formatted_tax_group_base_amount'] = formatLang(self.env, group['tax_group_base_amount'],
                                                                              currency_obj=move.additional_currency)

                        untaxed_amounts.append(group)

                    # Change Group with IQD Group
                    move.tax_totals_iqd['groups_by_subtotal']['Untaxed Amount'] = untaxed_amounts

            else:
                # Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
                move.tax_totals_iqd = None

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        for move in res:
            if move.currency_id.id != move.additional_currency.id:
                if move.additional_currency_rate_access:
                    if move.additional_currency_rate != move.get_currency_rate(move, move.currency_id,
                                                                               move.additional_currency):
                        move.create_new_currency_rate()
        return res

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        for move in self:
            if move.currency_id.id != move.additional_currency.id:
                if move.additional_currency_rate_access:
                    if move.additional_currency_rate != move.get_currency_rate(move, move.currency_id,
                                                                               move.additional_currency):
                        move.create_new_currency_rate()
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


class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = 'account.move.line'

    additional_currency = fields.Many2one('res.currency', related='move_id.additional_currency')
    price_unit_iqd = fields.Float('Price unit (IQD)', compute='compute_price_unit_iqd', digits=(12, 3))
    price_subtotal_iqd = fields.Float('Price Subtotal (IQD)', compute='compute_price_unit_iqd', digits=(12, 3))
    price_total_iqd = fields.Float('Price Total (IQD)', compute='compute_price_unit_iqd', digits=(12, 3))

    def compute_price_unit_iqd(self):
        for line in self:
            if line.move_id.id != line.move_id.additional_currency.id:
                line.price_unit_iqd = line.price_unit * line.move_id.additional_currency_rate
                line.price_subtotal_iqd = line.price_subtotal * line.move_id.additional_currency_rate
                line.price_total_iqd = line.price_total * line.move_id.additional_currency_rate
            else:
                line.price_unit_iqd = line.price_unit
                line.price_subtotal_iqd = line.price_subtotal
                line.price_total_iqd = line.price_total
