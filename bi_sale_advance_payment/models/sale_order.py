# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # name = fields.Char(string="English")
    # name_arabic = fields.Char(string="Arabic")
    # sale_order_line = fields.Many2one('sale.order.line')
    account_payment_ids = fields.Many2many('account.payment', 'sale_payment_rel', copy=False, readonly=True)
    total_advance_amount_payments = fields.Monetary(string='Total Payment',
                                                      compute='compute_total_advance_payment', store=True)

    @api.depends('account_payment_ids')
    def compute_total_advance_payment(self):
        for order in self:
            order.total_advance_amount_payments = sum(line.amount_company_currency_signed for line in order.account_payment_ids)



    def _confirmation_error_message(self):
        """ Return whether order can be confirmed or not if not then returm error message. """
        self.ensure_one()
        if self.state not in {'draft', 'sent', 'pre_confirm'}:
            return _("Some orders are not in a state requiring confirmation.")
        if any(
            not line.display_type
            and not line.is_downpayment
            and not line.product_id
            for line in self.order_line
        ):
            return _("Some order lines are missing a product, you need to correct them before going further.")

        return False