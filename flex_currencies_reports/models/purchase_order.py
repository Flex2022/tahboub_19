# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import file_open, formatLang
import json


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = 'purchase.order'

    def get_iqd_currency(self):
        return self.env.company.currency_id.id

    additional_currency = fields.Many2one('res.currency', string='Report Currency', default=get_iqd_currency)
    additional_currency_rate = fields.Float(string='Currency Rate', digits=(12, 12),
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
            if order.currency_id and order.additional_currency:
                order.additional_currency_rate = self.get_currency_rate(order, order.currency_id,
                                                                        order.additional_currency)

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
        res = super(PurchaseOrder, self).create(vals)
        if self.currency_id.id != self.additional_currency.id:
            if self.additional_currency_rate_access:
                if self.additional_currency_rate != self.get_currency_rate(self, self.currency_id,
                                                                           self.additional_currency):
                    self.create_new_currency_rate()
        return res

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
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
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['additional_currency_rate'] = self.additional_currency_rate
        res['additional_currency'] = self.additional_currency.id
        res['currency_id'] = self.currency_id.id
        return res


class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _inherit = 'purchase.order.line'

    additional_currency = fields.Many2one('res.currency', related='order_id.additional_currency')
    price_unit_iqd = fields.Float('Price unit (IQD)', compute='compute_price_unit_iqd')
    price_subtotal_iqd = fields.Float('Price Subtotal (IQD)', compute='compute_price_unit_iqd')
    price_total_iqd = fields.Float('Price Total (IQD)', compute='compute_price_unit_iqd')

    def compute_price_unit_iqd(self):
        for line in self:
            if line.order_id.id != line.order_id.additional_currency.id:
                line.price_unit_iqd = line.price_unit * line.order_id.additional_currency_rate
                line.price_subtotal_iqd = line.price_subtotal * line.order_id.additional_currency_rate
                line.price_total_iqd = line.price_total * line.order_id.additional_currency_rate

            else:
                line.price_unit_iqd = line.price_unit
                line.price_subtotal_iqd = line.price_subtotal
                line.price_total_iqd = line.price_total
