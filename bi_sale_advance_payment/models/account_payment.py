# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import fields, models, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    # sale_id = fields.Many2one('sale.order', string="Sale", readonly=True)
    sale_ids = fields.Many2many('sale.order', 'sale_payment_rel', copy=False)
    sale_count = fields.Integer('Sale Count', compute="_compute_sale_count")
    # total_sale = fields.Float('Total Sale', compute='_compute_total_sale',)
    remaining = fields.Float('Remaining', compute='_compute_remaining', store=True)
    pdc_wizard_id = fields.Many2one('pdc.wizard', string='PDC')
    new_tax = fields.Many2one('account.tax', string='Taxes')

    def delete_action(self):
        sale_id = self.env['sale.order'].browse(self.env.context.get('sale_id'))
        payment_invoice_ids = self.reconciled_invoice_ids.ids
        sale_invoice_ids = sale_id.invoice_ids.ids
        matched_ids = set(payment_invoice_ids) & set(sale_invoice_ids)
        if matched_ids:
            list_matched_ids = list(matched_ids)
            object_matched_ids = self.env['account.move'].browse(list_matched_ids)
            message = """"""
            for invoice in object_matched_ids:
                message += """\n{invoice_name}""".format(invoice_name=invoice.name)
            raise ValidationError(
                _('You can not delete this payment because its already link to invoice related to this sale order. \n\nPlease unlink this payment ({payment_name}) from these invoices first:'.format(
                    payment_name=self.name) + message))
        else:
            sale_id.account_payment_ids = [(3, self.id, 0)]

    @api.depends('move_id.line_ids')
    def _compute_remaining(self):
        for record in self:
            # Get receivable lines of the payment
            receivable_lines = record.move_id.line_ids.filtered(lambda l: l.account_id.internal_type == 'receivable')

            total_partial_reconcile = sum(
                self.env['account.partial.reconcile'].search([('credit_move_id', 'in', receivable_lines.ids)]).mapped(
                    'credit_amount_currency')
            )
            record.remaining = record.amount - total_partial_reconcile

    def _compute_sale_count(self):
        for record in self:
            record.sale_count = len(record.sale_ids)

    def button_open_sales(self):
        pass
        action = {
            'name': _("Sales"),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'context': {'create': False},
        }
        if len(self.sale_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.sale_ids.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', self.sale_ids.ids)],
            })
        return action

    # @api.depends('sale_ids')
    # def _compute_qty_invoiced(self):
    #     for record in self:
    #         record.qty_invoiced = sum(record.sale_ids.mapped('qty_invoiced'))
