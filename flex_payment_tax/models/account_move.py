# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    tax_payment_id = fields.Many2one(comodel_name='account.payment', string='Tax Payment', readonly=True, copy=False, check_company=True)


    def button_draft(self):
        ''' if self has payment_id then check if the payment has tax_move and also reset it to draft '''
        res = super(AccountMove, self).button_draft()
        for move in self.filtered(lambda m: m.move_type == 'entry' and m.origin_payment_id.tax_move_id):
            move.origin_payment_id.tax_move_id.button_draft()
        return res


class AccountPartialReconcile(models.Model):
    _inherit = 'account.partial.reconcile'

    reverse_tax_move = fields.Many2one(
        comodel_name='account.move', string='Reverse Tax Entry', readonly=True, copy=False, check_company=True)

    def unlink(self):
        for rec in self:
            # invoice = rec.debit_move_id.move_id.filtered(lambda move: move.move_type == 'out_invoice')
            # payment = rec.credit_move_id.move_id.payment_id
            # rec.reverse_tax_move.sudo().unlink()
            rec.reverse_tax_move.button_cancel()
        return super(AccountPartialReconcile, self).unlink()

    @api.model_create_multi
    def create(self, vals_list):
        create_partials = super(AccountPartialReconcile, self).create(vals_list)
        create_partials._generate_reverse_tax_move()
        return create_partials

    def _generate_reverse_tax_move(self):
        move_types = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
        for partial in self:
            invoice = partial.debit_move_id.move_id.filtered(lambda move: move.move_type in move_types)
            payment = partial.credit_move_id.move_id.origin_payment_id
            if not (invoice and payment) or not payment.tax_move_id:
                continue
            if payment.tax_move_id.state != 'posted':
                payment.tax_move_id.button_cancel()
            else:
                tax_clearing_account = self.company_id.payment_tax_account_id
                if not tax_clearing_account:
                    raise UserError(_('There is no tax clearing account set in the accounting settings.'))
                amount = partial.amount
                if payment.tax_id:
                    amount = partial.amount / ((payment.tax_id.amount + 100) * 0.01)
                move = self.env['account.move'].create({
                    'date': fields.Date.today(),
                    'move_type': 'entry',
                    'ref': payment.payment_reference,
                    'journal_id': payment.journal_id.id,
                    'partner_id': payment.partner_id.id,
                    'company_id': payment.company_id.id,
                    'tax_payment_id': payment.id,
                    'line_ids': [
                        (0, 0, {
                            'name': payment.payment_reference,
                            'date_maturity': fields.Date.today(),
                            'currency_id': payment.currency_id.id,
                            'debit': amount,
                            'credit': 0.0,
                            'partner_id': payment.partner_id.id,
                            'account_id': tax_clearing_account.id,
                            'tax_ids': [(6, 0, payment.tax_id.ids if payment.payment_type == 'outbound' else [])],
                        }),
                        (0, 0, {
                            'name': payment.payment_reference,
                            'date_maturity': fields.Date.today(),
                            'currency_id': payment.currency_id.id,
                            'debit': 0.0,
                            'credit': amount,
                            'partner_id': payment.partner_id.id,
                            'account_id': tax_clearing_account.id,
                            'tax_ids': [(6, 0, payment.tax_id.ids if payment.payment_type == 'inbound' else [])],
                        }),
                    ],
                })
                move.with_context(check_move_validity=False)._recompute_dynamic_lines()
                move._post(soft=False)
                partial.reverse_tax_move = move.id
