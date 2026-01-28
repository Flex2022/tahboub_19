# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError, UserError
from odoo import api, fields, models, _


class AdvancePayment(models.TransientModel):
    _name = 'advance.payment'
    _description = 'Advance Payment'

    def _get_total(self):
        order_id = self.env.context.get('active_id')
        order_model = self.env['sale.order'].browse(order_id)
        total = order_model.amount_total
        return total

    journal_id = fields.Many2one('account.journal', string="Payment Journal", required=True,
                                 domain=[('type', 'in', ['cash', 'bank'])])
    pay_amount = fields.Float(string="Payable Amount", required=True, digits=(16, 3))
    date_planned = fields.Datetime(string="Advance Payment Date", index=True, default=fields.Datetime.now,
                                   required=True)
    total = fields.Float('Total', default=_get_total, readonly=True, digits=(16, 3))
    create_invoice = fields.Selection([('full_invoice', 'Full Invoice Amount'), ('advance_payment', 'Advance Payment')],
                                      string='Create Invoice', required=True, default='full_invoice')
    auto_confirm = fields.Boolean('Auto Confirm Invoice')
    auto_link = fields.Boolean('Auto Link Payment')
    tax_id = fields.Many2one('account.tax', string='Taxes', context={'active_test': False}, check_company=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    tax_country_id = fields.Many2one('res.country', string='Tax Country', compute='_compute_tax_country_id')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)

    @api.depends('company_id')
    def _compute_tax_country_id(self):
        for rec in self:
            rec.tax_country_id = rec.company_id.country_id.id

    @api.constrains('pay_amount')
    def check_amount(self):
        if self.pay_amount <= 0:
            raise ValidationError(_("Please Enter Postive Amount"))
        if self.create_invoice == 'full_invoice':
            if self.pay_amount < self.total:
                raise ValidationError(_("Payable Amount Can Not Be Less Than Total"))

    def make_payment(self):
        self = self.sudo()
        payment_obj = self.env['account.payment']
        purchase_ids = self.env.context.get('active_ids', [])
        if purchase_ids:
            payment_res = self.get_payment(purchase_ids)
            payment = payment_obj.create(payment_res)
            payment.action_post()

        return {
            'type': 'ir.actions.act_window_close',
        }

    def get_payment(self, purchase_ids):
        purchase_obj = self.env['sale.order']
        purchase_id = purchase_ids[0]
        purchase = purchase_obj.browse(purchase_id)
        payment_res = {
            'payment_type': 'inbound',
            'partner_id': purchase.partner_id.id,
            'partner_type': 'customer',
            'journal_id': self[0].journal_id.id,
            'company_id': purchase.company_id.id,
            'currency_id': self.currency_id.id,
            'date': self[0].date_planned,
            'amount': self[0].pay_amount,
            'sale_ids': [purchase.id],
            'tax_id': self.tax_id.id,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id

        }
        # print(purchase.account_payment_ids)
        # self.env.cr.execute("""INSERT INTO sale_payment_rel (sale_order_id, account_payment_id) VALUES (%s, %s) """,
        #                     tuple((purchase.id, self.id)))
        return payment_res

    def make_payment_and_view_invoice(self):
        sale_order_id = self.env['sale.order'].browse(self.env.context.get('active_id'))
        sale_order_id.sudo().action_confirm()
        invoice_id = sale_order_id.sudo()._create_invoices()

        self = self.sudo()
        payment_obj = self.env['account.payment']
        purchase_ids = self.env.context.get('active_ids', [])
        if purchase_ids:
            payment_res = self.get_payment(purchase_ids)
            payment = payment_obj.create(payment_res)
            payment.action_post()

        if self.auto_confirm:
            invoice_id.action_post()
            if self.auto_link:
                receivable_line = payment.line_ids.filtered('credit')
                invoice_id.js_assign_outstanding_line(receivable_line.id)
        return sale_order_id.action_view_invoice()
