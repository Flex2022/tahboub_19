# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    use_payment_tax = fields.Boolean(related="company_id.use_payment_tax", string="Enable Tax Entry")
    tax_id = fields.Many2one(comodel_name="account.tax", string="Tax",
                             domain=[('type_tax_use', '=', 'sale'), ('amount_type', '=', 'percent')])
    tax_move_id = fields.Many2one(
        comodel_name='account.move', string='Tax Entry', readonly=True, copy=False, check_company=True)
    reverse_tax_moves = fields.One2many('account.move', 'tax_payment_id', string='Reverse Tax Entries')

    def _prepare_tax_move_vals(self):
        self.ensure_one()
        tax_clearing_account = self.company_id.payment_tax_account_id
        if not tax_clearing_account:
            raise UserError(_('There is no tax clearing account set in the accounting settings.'))
        # tax_amount = 0.0
        # if self.tax_id:
        #     taxes = self.tax_id.compute_all(self.amount, currency=self.currency_id, partner=self.partner_id)
        #     tax_amount = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
        amount = self.amount
        if self.tax_id:
            amount = self.amount / ((self.tax_id.amount + 100) * 0.01)
        move_lines = [
            (0, 0, {
                'name': self.payment_reference,
                'date_maturity': self.date,
                'currency_id': self.currency_id.id,
                'debit': amount,
                'credit': 0.0,
                'partner_id': self.partner_id.id,
                'account_id': tax_clearing_account.id,
                # 'account_id': self.outstanding_account_id.id,
                # 'recompute_tax_line': True,
                'tax_ids': [(6, 0, self.tax_id.ids if self.payment_type == 'inbound' else [])],
            }),
            (0, 0, {
                'name': self.payment_reference,
                'date_maturity': self.date,
                'currency_id': self.currency_id.id,
                'debit': 0.0,
                'credit': amount,
                'partner_id': self.partner_id.id,
                'account_id': tax_clearing_account.id,
                # 'account_id': self.outstanding_account_id.id,
                # 'recompute_tax_line': True,
                'tax_ids': [(6, 0, self.tax_id.ids if self.payment_type == 'outbound' else [])],
            }),
        ]
        move_vals = {
            'date': self.date,
            'move_type': 'entry',
            'ref': self.payment_reference,
            'journal_id': self.journal_id.id,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'line_ids': move_lines,
        }
        return move_vals

    def _create_tax_moves(self):
        move_obj = self.env['account.move']
        for pay in self:
            tax_moves = move_obj.create(pay._prepare_tax_move_vals())
            # tax_moves.with_context(check_move_validity=False)._move_autocomplete_invoice_lines_values()
            tax_moves.with_context(check_move_validity=False)._recompute_dynamic_lines()
            pay.tax_move_id = tax_moves.id
            if self._context.get('auto_post_tax_move', False):
                tax_moves._post(soft=False)

    def _update_tax_moves(self):
        for pay in self:
            tax_move_vals = pay._prepare_tax_move_vals()
            pay.tax_move_id.write({'line_ids': [(5,)]})
            pay.tax_move_id.write(tax_move_vals)
            # pay.tax_move_id.with_context(check_move_validity=False)._move_autocomplete_invoice_lines_values()
            pay.tax_move_id.with_context(check_move_validity=False)._recompute_dynamic_lines()

    def _create_or_update_tax_moves(self):
        need_create = self.filtered(lambda pay: not pay.tax_move_id)
        if need_create:
            need_create._create_tax_moves()
        need_update = self - need_create
        if need_update:
            need_update._update_tax_moves()

    @api.model_create_multi
    def create(self, vals_list):
        # Normalize company_id to ensure it's an ID, not a recordset
        for vals in vals_list:
            if 'company_id' in vals and hasattr(vals['company_id'], 'id'):
                vals['company_id'] = vals['company_id'].id
        payments = super(AccountPayment, self).create(vals_list)
        payments.filtered(lambda pay: pay.tax_id and pay.use_payment_tax and pay.amount != 0)._create_tax_moves()
        return payments

    def write(self, vals):
        res = super(AccountPayment, self).write(vals)
        if any(val in vals for val in ['tax_id', 'amount', 'journal_id', 'date', 'company_id']):
            need_create_or_update = self.filtered(lambda pay: pay.tax_id and pay.use_payment_tax and pay.amount != 0)
            need_create_or_update._create_or_update_tax_moves()
            need_remove = self - need_create_or_update
            if need_remove:
                need_remove.with_context(force_delete=True).tax_move_id.unlink()
        return res

    def action_cancel(self):
        ''' draft -> cancelled '''
        res = super(AccountPayment, self).action_cancel()
        self.tax_move_id.button_cancel()
        return res

    def action_post(self):
        ''' draft -> posted '''
        res = super(AccountPayment, self).action_post()
        self.tax_move_id._post(soft=False)
        return res

    def action_draft(self):
        ''' posted -> draft '''
        res = super(AccountPayment, self).action_draft()
        self.tax_move_id.button_draft()
        return res

    def unlink(self):
        if self.tax_move_id:
            self.with_context(force_delete=True).tax_move_id.unlink()
        return super(AccountPayment, self).unlink()

    def button_open_tax_entry(self):
        '''Open Tax Entry'''
        self.ensure_one()
        return {
            'name': _("Journal Entry"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
            'view_mode': 'form',
            'res_id': self.tax_move_id.id,
        }

    def button_open_reverse_tax_entry(self):
        '''Open Reverse Tax Entry'''
        self.ensure_one()
        return {
            'name': _("Reversed Tax Moves"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
            'view_mode': 'list,form',
            'domain': [('tax_payment_id', 'in', self.ids)],
        }
