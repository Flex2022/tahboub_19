# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    payment_journal_id = fields.Many2one(
        'account.journal', string="Payment Journal", domain=[('type', 'in', ['cash', 'bank'])])
    date_accounting = fields.Date('Accounting Date', default=fields.Date.today)
    is_down_payment = fields.Boolean()

    @api.constrains('fixed_amount')
    def check_amount_gt_zero(self):
        if self.is_down_payment and self.fixed_amount <= 0:
            raise ValidationError(_("Amount Should be positive."))

    def _prepare_invoice_values(self, order, name, amount, so_line):
        res = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)
        if self.is_down_payment:
            res.update({'invoice_date': self.date_accounting})
        return res

    def create_invoices(self):

        res = super(SaleAdvancePaymentInv, self).create_invoices()
        sale_id = self.env.context.get('active_id', False)
        current_so = self.env['sale.order'].browse(sale_id)
        paid_as_down_payment = sum(current_so.account_payment_ids.mapped('amount'))
        if self.advance_payment_method == 'delivered' and not current_so.partner_id.credit_check and current_so.amount_total > paid_as_down_payment:
            raise UserError(_('You have to pay the whole amount first'))

        if self.is_down_payment and sale_id:

            payment_vals = self.prepare_payment_vals(sale_id)
            self = self.sudo()
            payment = self.env['account.payment'].create(payment_vals)
            payment.action_post()
            current_so.action_confirm()
            return payment
        return res

    def prepare_payment_vals(self, sale_id):
        purchase_obj = self.env['sale.order']
        sale_id = sale_id
        so = purchase_obj.browse(sale_id)
        payment_vals = {
            'payment_type': 'inbound',
            'partner_id': so.partner_id.id,
            'partner_type': 'customer',
            'journal_id': self.payment_journal_id.id,
            'company_id': so.company_id,
            'currency_id': so.currency_id.id,
            'date': self.date_accounting,
            'amount': self.fixed_amount,
            'sale_id': so.id,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id
        }
        return payment_vals
