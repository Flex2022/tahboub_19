# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError
import json


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_invoiced = fields.Float(string='Invoiced Amount', compute='_get_amount_invoiced')
    amount_paid = fields.Float(string='Paid Amount', compute='_get_amount_invoiced')
    amount_remaining = fields.Float(string='Remaining Amount', compute='_get_amount_remaining')

    # def action_confirm(self):
    #     if not self.partner_id.credit_check and not self.account_payment_ids.filtered(lambda p: p.state == 'posted'):
    #         # return self.env.ref('bi_sale_advance_payment.action_advance_payment_wizard_form').read()[0]
    #         action = self.sudo().env.ref('hz_sale_down_payment.action_sale_advance_payment_inv').read()[0]
    #         if self.env.user.restrict_journals:
    #             allowed_journal_ids = self.env.user.allowed_journals.filtered(
    #                 lambda j: j.company_id == self.company_id).ids
    #         else:
    #             allowed_journal_ids = self.sudo().env['account.journal'].search(
    #                 [('company_id', '=', self.company_id.id), ('type', 'in', ['cash', 'bank'])]).ids
    #         action['context'] = {'default_is_down_payment': True,
    #                              'default_advance_payment_method': 'fixed',
    #                              'allowed_journal_ids': allowed_journal_ids, }
    #         return action
    #     else:
    #         return super(SaleOrder, self).action_confirm()

    @api.depends('invoice_ids.state', 'invoice_ids.amount_total', 'invoice_ids.amount_residual')
    def _get_amount_invoiced(self):
        for rec in self:
            rec.amount_invoiced = sum(rec.invoice_ids.filtered(lambda inv: inv.state != 'cancel').mapped('amount_total'))
            rec.amount_paid = sum(rec.invoice_ids.filtered(lambda inv: inv.state == 'posted').mapped('amount_total')) - \
                              sum(rec.invoice_ids.filtered(lambda inv: inv.state == 'posted').mapped('amount_residual'))

    @api.depends('amount_total', 'amount_invoiced')
    def _get_amount_remaining(self):
        for rec in self:
            rec.amount_remaining = rec.amount_total - rec.amount_invoiced

    def bi_action_advance_payment_wizard_form(self):
        action = self.sudo().env.ref('bi_sale_advance_payment.action_advance_payment_wizard_form').read()[0]
        if self.env.user.restrict_journals:
            allowed_journal_ids = self.env.user.allowed_journals.filtered(
                lambda j: j.company_id == self.company_id).ids
        else:
            allowed_journal_ids = self.sudo().env['account.journal'].search(
                [('company_id', '=', self.company_id.id), ('type', 'in', ['cash', 'bank'])]).ids
        action['context'] = {'allowed_journal_ids': allowed_journal_ids, }
        return action
