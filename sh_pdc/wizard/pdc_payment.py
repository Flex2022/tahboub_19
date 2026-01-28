# Copyright (C) Softhealer Technologies.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from datetime import timedelta
from odoo.tools import float_is_zero, float_compare


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    pdc_id = fields.Many2one('pdc.wizard')


class PDC_wizard(models.Model):
    _name = "pdc.wizard"
    _description = "PDC Wizard"

    def open_attachments(self):
        # [action] = self.env.ref('base.action_attachment').read()
        action = self.env["ir.actions.actions"]._for_xml_id("base.action_attachment")
        ids = self.env['ir.attachment'].search([('pdc_id', '=', self.id)])
        id_list = []
        for pdc_id in ids:
            id_list.append(pdc_id.id)
        action['domain'] = [('id', 'in', id_list)]
        return action

    def open_journal_items(self):
        # [action] = self.env.ref('account.action_account_moves_all').read()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_account_moves_all")
        ids = self.env['account.move.line'].search([('pdc_id', '=', self.id)])
        id_list = []
        for pdc_id in ids:
            id_list.append(pdc_id.id)
        action['domain'] = [('id', 'in', id_list)]
        return action

    def open_journal_entry(self):
        # [action] = self.env.ref('sh_pdc.sh_pdc_action_move_journal_line').read()
        action = self.env["ir.actions.actions"]._for_xml_id("sh_pdc.sh_pdc_action_move_journal_line")
        ids = self.env['account.move'].search([('pdc_id', '=', self.id)])
        id_list = []
        for pdc_id in ids:
            id_list.append(pdc_id.id)
        action['domain'] = [('id', 'in', id_list)]
        return action

    @api.model
    def default_get(self, fields):
        rec = super(PDC_wizard, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.move':
            return rec
        invoices = self.env['account.move'].browse(active_ids)
        if invoices:
            invoice = invoices[0]
            if invoice.move_type in ('out_invoice', 'out_refund'):
                rec.update({'payment_type': 'receive_money'})
            elif invoice.move_type in ('in_invoice', 'in_refund'):
                rec.update({'payment_type': 'send_money'})

            rec.update({'partner_id': invoice.partner_id.id,
                        'payment_amount': invoice.amount_residual,
                        'invoice_id': invoice.id,
                        'due_date': invoice.invoice_date_due,
                        'memo': invoice.name})

        return rec

    name = fields.Char("Name", default='New', readonly=1)
    # check_amount_in_words = fields.Char(string="Amount in Words",compute='_compute_check_amount_in_words')
    payment_type = fields.Selection([('receive_money', 'Receive Money'), (
        'send_money', 'Send Money')], string="Payment Type", default='receive_money')
    register_partner_account = fields.Selection([('partner', 'Partner'), (
        'account', 'Account')], string="Register By", default='partner')
    partner_id = fields.Many2one('res.partner', string="Partner")
    account_id = fields.Many2one('account.account', string="Account")
    payment_amount = fields.Monetary("Payment Amount")
    currency_id = fields.Many2one(
        'res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    reference = fields.Char("Cheque Reference")
    journal_id = fields.Many2one('account.journal', string="Payment Journal", domain=[
        ('type', '=', 'bank')], )
    account_id_under_collection = fields.Many2one('account.account', string="Under Collection Account")
    cheque_status = fields.Selection([('draft', 'Draft'), ('deposit', 'Deposit'), ('paid', 'Paid')],
                                     string="Cheque Status", default='draft')
    payment_date = fields.Date(
        "Payment Date", default=fields.Date.today(), required=1)
    due_date = fields.Date("Due Date")
    actual_date = fields.Date("Actual Date", copy=False)
    memo = fields.Char("Memo")
    agent = fields.Char("Agent")
    bank_id = fields.Many2one('res.bank', string="Bank")
    attachment_ids = fields.Many2many('ir.attachment', string='Cheque Image')
    company_id = fields.Many2one('res.company', string='company', default=lambda self: self.env.company)
    invoice_id = fields.Many2one('account.move', string="Invoice/Bill")
    state = fields.Selection([('draft', 'Draft'), ('registered', 'Registered'), ('returned', 'Returned'),
                              ('under_collection', 'Under Collection'), ('deposited', 'Deposited'),
                              ('bounced', 'Bounced'), ('done', 'Done'), ('posted', 'Parent Posted'),
                              ('cancel', 'Cancelled')], string="State",
                             default='draft')
    line_ids = fields.One2many(
        'pdc.wizard',
        'parent_id',
        string='SubCheques',
        help='Help text for your field'
    )

    # Optional: If you want to add a parent field for the inverse relationship
    parent_id = fields.Many2one(
        'pdc.wizard',
        string='PDC Group',
        help='Reference to the parent wizard'
    )

    pdc_group = fields.Boolean(string="IS PDC Group ?", default=False)

    @api.onchange('register_partner_account')
    def onchange_register_partner_account(self):
        for pdc in self:
            if pdc.register_partner_account == 'partner':
                pdc.account_id = False
            else:
                pdc.partner_id = False

    @api.constrains('pdc_group', 'line_ids')
    def _check_line_ids(self):
        for record in self:
            if record.pdc_group and not record.line_ids:
                raise ValidationError(_("SubCheques are required for PDC Groups."))

    @api.onchange('register_partner_account')
    def onchange_line_ids(self):
        for pdc in self:
            if pdc.register_partner_account == 'partner':
                pdc.account_id = False
            else:
                pdc.parent_id = False

    @api.onchange('line_ids')
    def onchange_line_ids(self):
        for pdc in self:
            if pdc.line_ids:
                pdc.due_date = False

    def action_open(self):
        return {
            'name': 'SubCheques',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'pdc.wizard',
            'res_id': self.id,
            'view_id': self.env.ref('sh_pdc.sh_pdc_payment_form_view').id,
            'target': 'new',
        }

    deposited_debit = fields.Many2one('account.move.line')
    deposited_credit = fields.Many2one('account.move.line')
    tax_id = fields.Many2one(comodel_name="account.tax", string="Tax",
                             domain=[('type_tax_use', '=', 'sale'), ('amount_type', '=', 'percent')])
    account_payment_id = fields.Many2one('account.payment', index=True, store=True,
                                         string="Payment",
                                         help="The payment that created this entry")
    tax_move_id = fields.Many2one(
        comodel_name='account.move', related="account_payment_id.tax_move_id", string='Tax Entry', readonly=True,
        copy=False, check_company=True)

    # attachment_ids = fields.One2many(
    #    'ir.attachment', 'pdc_id', string="Attachments")

    #     def _compute_check_amount_in_words(self):
    #         if self:
    #             for rec in self:
    #                 rec.check_amount_in_words = False
    #                 rec.check_amount_in_words = rec.currency_id.amount_to_text(rec.payment_amount)

    # Register pdc payment
    def button_register(self):
        if self:
            if self.cheque_status == 'draft':
                self.write({'state': 'draft'})

            if self.cheque_status == 'deposit':
                self.action_register()
                self.action_deposited()
                self.write({'state': 'deposited'})

            if self.cheque_status == 'paid':
                self.action_register()
                self.action_deposited()
                self.action_done()
                self.write({'state': 'done'})

    #             if self.invoice_id:
    #                 self.invoice_id.sudo().write({
    # #                     'amount_residual_signed': self.invoice_id.amount_residual_signed - self.payment_amount,
    #                     'amount_residual':self.invoice_id.amount_residual - self.payment_amount,
    #                     })
    #                 self.invoice_id._compute_amount()
    #

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

    def action_register(self):
        if self.line_ids:
            self.state = "posted"
            for line in self.line_ids:
                line.action_register()
        else:
            if not self.journal_id:
                raise ValidationError(_('Please Enter Payment Journal First!'))
            move = self.env['account.move']

            self.check_payment_amount()  # amount must be positive
            pdc_account = self.check_pdc_account()
            partner_account = self.get_partner_account()

            # Create Journal Item
            move_line_vals_debit = {}
            move_line_vals_credit = {}
            if self.payment_type == 'receive_money':
                move_line_vals_debit = self.get_debit_move_line(pdc_account, self.payment_date)
                move_line_vals_credit = self.get_credit_move_line(partner_account, self.payment_date)
            else:
                move_line_vals_debit = self.get_debit_move_line(partner_account, self.payment_date)
                move_line_vals_credit = self.get_credit_move_line(pdc_account, self.payment_date)

            # create move and post it
            move_vals = self.get_move_vals(move_line_vals_debit, move_line_vals_credit, self.payment_date)
            move_id = move.create(move_vals)
            move_id.action_post()
            self.write({'state': 'registered'})

            if self.register_partner_account == 'partner':
                self.account_payment_id = self.env['account.payment'].create({
                    'payment_type': 'outbound' if self.payment_type == 'send_money' else 'inbound',
                    'partner_type': 'supplier' if self.payment_type == 'send_money' else 'customer',
                    'partner_id': self.partner_id.id,
                    'amount': self.payment_amount,
                    'currency_id': self.env.company.currency_id.id,
                    'date': self.payment_date,
                    'payment_reference': self.memo,
                    'journal_id': self.journal_id.id,
                    'pdc_wizard_id': self.id,
                    'tax_id': self.tax_id.id,
                })
                # make it posted
                self.account_payment_id.action_post()
                old_move_id = self.account_payment_id.move_id
                new_move_id = move_id
                self.account_payment_id.move_id = new_move_id
                old_move_id.with_context(force_delete=True).unlink()

    def check_payment_amount(self):
        if self.payment_amount <= 0.0:
            raise UserError("Amount must be greater than zero!")

    def check_pdc_account(self):
        # if self.register_partner_account == 'account':
        #     return self.account_id.id
        if self.payment_type == 'receive_money':
            if not self.env.company.pdc_customer:
                raise UserError(
                    "Please Set PDC payment account for Customer !")
            else:
                return self.env.company.pdc_customer.id

        else:
            if not self.env.company.pdc_vendor:
                raise UserError(
                    "Please Set PDC payment account for Supplier !")
            else:
                return self.env.company.pdc_vendor.id

    def get_partner_account(self):
        if self.register_partner_account == 'account':
            return self.account_id.id
        if self.payment_type == 'receive_money':
            return self.partner_id.property_account_receivable_id.id
        else:
            return self.partner_id.property_account_payable_id.id

    # @api.onchange('line_ids', 'line_ids.payment_amount')
    @api.onchange('line_ids', 'line_ids')
    def onchange_line_ids(self):
        for pdc in self:
            if pdc.line_ids:
                total_amount = sum(pdc.line_ids.mapped('payment_amount'))
                total_amount = round(total_amount, 4)
                if pdc.payment_amount < total_amount:
                    raise ValidationError(
                        "Total payment amount in lines ({}) should not exceed the entered payment amount ({}).".format(
                            total_amount, pdc.payment_amount))

    # @api.constrains('line_ids', 'line_ids.payment_amount', 'payment_amount')
    @api.constrains('line_ids', 'line_ids', 'payment_amount')
    def check_payment_amount_consistency(self):
        for pdc in self:
            if pdc.line_ids:
                total_amount = sum(pdc.line_ids.mapped('payment_amount'))
                total_amount = round(total_amount, 4)
                if not float_compare(pdc.payment_amount, total_amount, precision_digits=4) == 0:
                    raise ValidationError(
                        "Total payment amount must be equal to the sum of line payment amounts."
                    )

    def action_returned(self):
        move = self.env['account.move']

        self.check_payment_amount()  # amount must be positive
        pdc_account = self.check_pdc_account()
        partner_account = self.get_partner_account()

        # Create Journal Item
        move_line_vals_debit = {}
        move_line_vals_credit = {}
        if self.payment_type == 'receive_money':
            move_line_vals_debit = self.get_debit_move_line(partner_account, self.payment_date)
            move_line_vals_credit = self.get_credit_move_line(pdc_account, self.payment_date)
        else:
            move_line_vals_debit = self.get_debit_move_line(pdc_account, self.payment_date)
            move_line_vals_credit = self.get_credit_move_line(partner_account, self.payment_date)

        # create move and post it
        move_vals = self.get_move_vals(move_line_vals_debit, move_line_vals_credit, self.payment_date)
        move_id = move.create(move_vals)
        move_id.action_post()

        self.write({'state': 'returned'})

        # cancel payment
        # self.account_payment_id.action_cancel()
        # self.account_payment_id = False
        # if self.tax_move_id:
        #     self.tax_move_id.action_cancel()

    def get_credit_move_line(self, account, date):

        entry = {'pdc_id': self.id,
                 'partner_id': self.partner_id.id,
                 'account_id': account,
                 'debit': 0.0,
                 'credit': self.payment_amount if self.currency_id == self.company_id.currency_id else self.payment_amount / self.currency_id.rate,
                 'currency_id': self.currency_id.id,
                 'ref': self.memo,
                 'date': date,
                 'date_maturity': self.due_date,
                 }
        if self.currency_id != self.company_id.currency_id:
            entry['amount_currency'] = - self.payment_amount

        return entry

    def get_debit_move_line(self, account, date):

        entry = {
            'pdc_id': self.id,
            'partner_id': self.partner_id.id,
            'account_id': account,
            'credit': 0.0,
            'debit': self.payment_amount if self.currency_id == self.company_id.currency_id else self.payment_amount / self.currency_id.rate,
            'currency_id': self.currency_id.id,
            'ref': self.memo,
            'date': date,
            'date_maturity': self.due_date,
        }
        if self.currency_id != self.company_id.currency_id:
            entry['amount_currency'] = self.payment_amount
        return entry

    def get_move_vals(self, debit_line, credit_line, date):
        return {
            'pdc_id': self.id,
            'date': date,
            'journal_id': self.journal_id.id,
            #             'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'ref': self.memo,
            'line_ids': [(0, 0, debit_line),
                         (0, 0, credit_line)]
        }

    # line.amount_currency = line.currency_id.round(line.balance * line.currency_rate)

    def action_deposited(self):
        if not self.account_id_under_collection:
            raise UserError(
                "Please Set Under Collection account!")
        move = self.env['account.move']

        self.check_payment_amount()  # amount must be positive
        pdc_account = self.check_pdc_account()
        partner_account = self.get_partner_account()

        # Create Journal Item
        move_line_vals_debit = {}
        move_line_vals_credit = {}
        if self.payment_type == 'receive_money':
            move_line_vals_debit = self.get_debit_move_line(self.account_id_under_collection.id, self.payment_date)
            move_line_vals_credit = self.get_credit_move_line(pdc_account, self.payment_date)
        else:
            # move_line_vals_debit = self.get_debit_move_line(partner_account, self.payment_date)
            # move_line_vals_credit = self.get_credit_move_line(pdc_account, self.payment_date)
            # todo: issue was here, (to be ensured)
            move_line_vals_debit = self.get_debit_move_line(pdc_account, self.payment_date)
            move_line_vals_credit = self.get_credit_move_line(self.account_id_under_collection.id, self.payment_date)

        # create move and post it
        move_vals = self.get_move_vals(
            move_line_vals_debit, move_line_vals_credit, self.payment_date)
        move_id = move.create(move_vals)
        move_id.action_post()

        self.write({'state': 'deposited', 'deposited_debit': move_id.line_ids.filtered(lambda x: x.debit > 0),
                    'deposited_credit': move_id.line_ids.filtered(lambda x: x.credit > 0)})

    def action_under_collection(self):
        move = self.env['account.move']

        self.check_payment_amount()  # amount must be positive
        partner_account = self.get_partner_account()
        if not self.under_collectionـjournal_id.default_account_id.id:
            raise UserError("Please Define under collection account!")

        # Create Journal Item
        move_line_vals_debit = {}
        move_line_vals_credit = {}
        move_line_vals_debit = self.get_debit_move_line(self.under_collectionـjournal_id.default_account_id.id)
        move_line_vals_credit = self.get_credit_move_line(partner_account)

        # create move and post it
        move_vals = self.get_move_vals(
            move_line_vals_debit, move_line_vals_credit)
        move_id = move.create(move_vals)
        move_id.action_post()

        self.write({'state': 'under_collection'})

    def action_bounced(self):
        move = self.env['account.move']

        self.check_payment_amount()  # amount must be positive
        pdc_account = self.check_pdc_account()
        partner_account = self.get_partner_account()

        # Create Journal Item
        move_line_vals_debit = {}
        move_line_vals_credit = {}

        if self.payment_type == 'receive_money':
            move_line_vals_debit = self.get_debit_move_line(pdc_account, self.due_date)
            move_line_vals_credit = self.get_credit_move_line(self.account_id_under_collection.id, self.due_date)
        else:
            move_line_vals_debit = self.get_credit_move_line(pdc_account, self.due_date)
            move_line_vals_credit = self.get_debit_move_line(self.account_id_under_collection.id, self.due_date)

        if self.memo:
            move_line_vals_debit.update(
                {
                    'name': f"PDC Payment : {self.memo}, Cheque# : {self.reference}, Date : {self.payment_date}, Due : {self.due_date}"})
            move_line_vals_credit.update(
                {
                    'name': f"PDC Payment : {self.memo}, Cheque# : {self.reference}, Date : {self.payment_date}, Due : {self.due_date}"})
        else:
            move_line_vals_debit.update(
                {'name': f"PDC Payment, Cheque# : {self.reference}, Date : {self.payment_date}, Due : {self.due_date}"})
            move_line_vals_credit.update(
                {'name': f"PDC Payment, Cheque# : {self.reference}, Date : {self.payment_date}, Due : {self.due_date}"})
        # create move and post it
        move_vals = self.get_move_vals(
            move_line_vals_debit, move_line_vals_credit, self.due_date)
        move_id = move.create(move_vals)
        move_id.action_post()

        self.write({'state': 'bounced'})

        # cancel payment
        # self.account_payment_id.action_cancel()
        # self.account_payment_id = False
        # if self.tax_move_id:
        #     self.tax_move_id.action_cancel()

    def action_done(self):
        if not self.actual_date:
            return {
                'name': _('Add Actual Date'),
                'view_mode': 'form',
                'res_model': 'pdc.actual.date.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'default_sh_pdc_id': self.id},  # Pass the sh_pdc_id to the wizard
            }
        else:
            if self.payment_type == 'receive_money':
                pmls = self.journal_id.inbound_payment_method_line_ids
            else:
                pmls = self.journal_id.outbound_payment_method_line_ids
            bank_account = pmls.mapped('payment_account_id')[:1]
            if not bank_account:
                raise UserError('No outstanding payment account found for the selected journal.')

            bank_account = bank_account.id
            move = self.env['account.move']
            self.check_payment_amount()  # amount must be positive
            # pdc_account = self.check_pdc_account()
            # bank_account = self.journal_id.payment_debit_account_id.id or self.journal_id.payment_credit_account_id.id

            # Create Journal Item
            move_line_vals_debit = {}
            move_line_vals_credit = {}
            if self.payment_type == 'receive_money':

                move_line_vals_debit = self.get_debit_move_line(bank_account, self.due_date)
                move_line_vals_credit = self.get_credit_move_line(self.account_id_under_collection.id, self.due_date)
            else:
                # move_line_vals_debit = self.get_debit_move_line(pdc_account, self.due_date)
                # move_line_vals_credit = self.get_credit_move_line(bank_account, self.due_date)
                move_line_vals_debit = self.get_debit_move_line(self.account_id_under_collection.id, self.due_date)
                move_line_vals_credit = self.get_credit_move_line(bank_account, self.due_date)

            if self.memo:
                # move_line_vals_debit.update({'name': 'PDC Payment :'+self.memo + ", Cheque# : " + self.reference + " , Date : " + str(self.payment_date) + ", Due : " + str(self.due_date),'partner_id':self.partner_id.id})
                move_line_vals_debit.update({
                    'name': f'PDC Payment: {self.memo}, Cheque#: {self.reference}, Date: {str(self.payment_date)}, Due: {str(self.due_date)}',
                    'partner_id': self.partner_id.id})
                # move_line_vals_credit.update({'name': 'PDC Payment :'+self.memo + ", Cheque# : " + self.reference + " , Date : " + str(self.payment_date) + ", Due : " + str(self.due_date),'partner_id':self.partner_id.id})
                move_line_vals_credit.update({
                    'name': f'PDC Payment: {self.memo}, Cheque#: {self.reference}, Date: {str(self.payment_date)}, Due: {str(self.due_date)}',
                    'partner_id': self.partner_id.id})
            else:
                # move_line_vals_debit.update({'name': 'PDC Payment' + ", Cheque# : " + self.reference + " , Date : " + str(self.payment_date) + ", Due : " + str(self.due_date),'partner_id':self.partner_id.id})
                move_line_vals_debit.update({
                    'name': f'PDC Payment, Cheque#: {self.reference}, Date: {str(self.payment_date)}, Due: {str(self.due_date)}',
                    'partner_id': self.partner_id.id})
                # move_line_vals_credit.update({'name': 'PDC Payment' + ", Cheque# : " + self.reference + " , Date : " + str(self.payment_date) + ", Due : " + str(self.due_date),'partner_id':self.partner_id.id})
                move_line_vals_credit.update({
                    'name': f'PDC Payment, Cheque#: {self.reference}, Date: {str(self.payment_date)}, Due: {str(self.due_date)}',
                    'partner_id': self.partner_id.id})

            # create move and post it
            move_vals = self.get_move_vals(move_line_vals_debit, move_line_vals_credit, self.actual_date)
            move_id = move.create(move_vals)
            move_id.action_post()

            invoice = self.env['account.move'].sudo().search(
                [('name', '=', self.memo), ('company_id', '=', self.company_id.id)])
            if invoice:

                if self.payment_type == 'receive_money':
                    # reconcilation Entry for Invoice
                    debit_move_id = self.env['account.move.line'].sudo().search([('move_id', '=', invoice.id),
                                                                                 ('debit', '>', 0.0)], limit=1)

                    credit_move_id = self.env['account.move.line'].sudo().search([('move_id', '=', move_id.id),
                                                                                  ('credit', '>', 0.0)], limit=1)

                    print("\n\n\n", debit_move_id, credit_move_id, self.deposited_credit, self.deposited_debit)
                    if debit_move_id and credit_move_id:
                        full_reconcile_id = self.env['account.full.reconcile'].sudo().create({})
                        amount = 0.0
                        if move_line_vals_debit['debit'] > 0.0:
                            amount = move_line_vals_debit['debit']
                        else:
                            amount = move_line_vals_debit['credit']
                        reconcile_id = self.env['account.partial.reconcile'].sudo().create(
                            {'debit_move_id': debit_move_id.id,
                             'credit_move_id': self.deposited_credit.id,
                             'amount': amount,
                             'debit_amount_currency': amount
                             })

                        reconcile_id = self.env['account.partial.reconcile'].sudo().create(
                            {'debit_move_id': self.deposited_debit.id,
                             'credit_move_id': credit_move_id.id,
                             'amount': amount,
                             'debit_amount_currency': amount
                             })
                else:
                    # reconcilation Entry for Invoice
                    credit_move_id = self.env['account.move.line'].sudo().search([('move_id', '=', invoice.id),
                                                                                  ('credit', '>', 0.0)], limit=1)

                    debit_move_id = self.env['account.move.line'].sudo().search([('move_id', '=', move_id.id),
                                                                                 ('debit', '>', 0.0)], limit=1)

                    if debit_move_id and credit_move_id:
                        amount = 0.0
                        if move_line_vals_debit['debit'] > 0.0:
                            amount = move_line_vals_debit['debit']
                        else:
                            amount = move_line_vals_debit['credit']
                        reconcile_id = self.env['account.partial.reconcile'].sudo().create(
                            {'debit_move_id': self.deposited_debit.id,
                             'credit_move_id': credit_move_id.id,
                             'amount': amount,
                             'credit_amount_currency': amount
                             })
                        reconcile_id = self.env['account.partial.reconcile'].sudo().create(
                            {'debit_move_id': debit_move_id.id,
                             'credit_move_id': self.deposited_credit.id,
                             'amount': amount,
                             'debit_amount_currency': amount
                             })

            self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.onchange('attachment_ids', 'partner_id')
    def onchange_attachment_ids(self):
        for pdc in self:
            for attachment in pdc.attachment_ids:
                attachment.res_id = pdc.id

    @api.model
    def create(self, vals_list):
        # vals_list is now a list of dicts
        for vals in vals_list:
            if vals.get('payment_type') == 'receive_money':
                vals['name'] = self.env['ir.sequence'].next_by_code('pdc.payment.customer')
            elif vals.get('payment_type') == 'send_money':
                vals['name'] = self.env['ir.sequence'].next_by_code('pdc.payment.vendor')

        res = super(PDC_wizard, self).create(vals_list)

        for pdc in res:
            for attachment in pdc.attachment_ids:
                attachment.res_id = pdc.id

        return res

    # ==============================
    #    CRON SCHEDULER CUSTOMER
    # ==============================
    @api.model
    def notify_customer_due_date(self):
        emails = []
        if self.env.company.is_cust_due_notify:
            notify_day_1 = self.env.company.notify_on_1
            notify_day_2 = self.env.company.notify_on_2
            notify_day_3 = self.env.company.notify_on_3
            notify_day_4 = self.env.company.notify_on_4
            notify_day_5 = self.env.company.notify_on_5
            notify_date_1 = False
            notify_date_2 = False
            notify_date_3 = False
            notify_date_4 = False
            notify_date_5 = False
            if notify_day_1:
                notify_date_1 = fields.date.today() + timedelta(days=int(notify_day_1) * -1)
            if notify_day_2:
                notify_date_2 = fields.date.today() + timedelta(days=int(notify_day_2) * -1)
            if notify_day_3:
                notify_date_3 = fields.date.today() + timedelta(days=int(notify_day_3) * -1)
            if notify_day_4:
                notify_date_4 = fields.date.today() + timedelta(days=int(notify_day_4) * -1)
            if notify_day_5:
                notify_date_5 = fields.date.today() + timedelta(days=int(notify_day_5) * -1)

            records = self.search([('payment_type', '=', 'receive_money')])
            for user in self.env.company.sh_user_ids:
                if user.partner_id and user.partner_id.email:
                    emails.append(user.partner_id.email)
            email_values = {
                'email_to': ','.join(emails),
            }
            view = self.env.ref("sh_pdc.sh_pdc_payment_form_view", raise_if_not_found=False).sudo()
            view_id = view.id if view else 0
            for record in records:
                if (record.due_date == notify_date_1
                        or record.due_date == notify_date_2
                        or record.due_date == notify_date_3
                        or record.due_date == notify_date_4
                        or record.due_date == notify_date_5):

                    if self.env.company.is_notify_to_customer:
                        template_download_id = record.env['ir.model.data'].get_object(
                            'sh_pdc', 'sh_pdc_company_to_customer_notification_1'
                        )
                        _ = record.env['mail.template'].browse(
                            template_download_id.id
                        ).send_mail(record.id, notif_layout='mail.mail_notification_light', force_send=True)
                    if self.env.company.is_notify_to_user and self.env.company.sh_user_ids:
                        url = ''
                        base_url = request.env['ir.config_parameter'].sudo(
                        ).get_param('web.base.url')
                        url = base_url + "/web#id=" + \
                              str(record.id) + \
                              "&&model=pdc.wizard&view_type=form&view_id=" + str(view_id)
                        ctx = {
                            "customer_url": url,
                        }
                        template_download_id = record.env['ir.model.data'].get_object(
                            'sh_pdc', 'sh_pdc_company_to_int_user_notification_1'
                        )
                        _ = request.env['mail.template'].sudo().browse(template_download_id.id).with_context(
                            ctx).send_mail(
                            record.id, email_values=email_values, notif_layout='mail.mail_notification_light',
                            force_send=True)

    # ==============================
    #    CRON SCHEDULER VENDOR
    # ==============================
    @api.model
    def notify_vendor_due_date(self):
        emails = []
        if self.env.company.is_vendor_due_notify:
            notify_day_1_ven = self.env.company.notify_on_1_vendor
            notify_day_2_ven = self.env.company.notify_on_2_vendor
            notify_day_3_ven = self.env.company.notify_on_3_vendor
            notify_day_4_ven = self.env.company.notify_on_4_vendor
            notify_day_5_ven = self.env.company.notify_on_5_vendor
            notify_date_1_ven = False
            notify_date_2_ven = False
            notify_date_3_ven = False
            notify_date_4_ven = False
            notify_date_5_ven = False
            if notify_day_1_ven:
                notify_date_1_ven = fields.date.today() + timedelta(days=int(notify_day_1_ven) * -1)
            if notify_day_2_ven:
                notify_date_2_ven = fields.date.today() + timedelta(days=int(notify_day_2_ven) * -1)
            if notify_day_3_ven:
                notify_date_3_ven = fields.date.today() + timedelta(days=int(notify_day_3_ven) * -1)
            if notify_day_4_ven:
                notify_date_4_ven = fields.date.today() + timedelta(days=int(notify_day_4_ven) * -1)
            if notify_day_5_ven:
                notify_date_5_ven = fields.date.today() + timedelta(days=int(notify_day_5_ven) * -1)

            records = self.search([('payment_type', '=', 'send_money')])
            for user in self.env.company.sh_user_ids_vendor:
                if user.partner_id and user.partner_id.email:
                    emails.append(user.partner_id.email)
            email_values = {
                'email_to': ','.join(emails),
            }
            view = self.env.ref("sh_pdc.sh_pdc_payment_form_view", raise_if_not_found=False)
            view_id = view.id if view else 0
            for record in records:
                if (record.due_date == notify_date_1_ven
                        or record.due_date == notify_date_2_ven
                        or record.due_date == notify_date_3_ven
                        or record.due_date == notify_date_4_ven
                        or record.due_date == notify_date_5_ven):

                    if self.env.company.is_notify_to_vendor:
                        template_download_id = record.env['ir.model.data'].get_object(
                            'sh_pdc', 'sh_pdc_company_to_customer_notification_1'
                        )
                        _ = record.env['mail.template'].browse(
                            template_download_id.id
                        ).send_mail(record.id, notif_layout='mail.mail_notification_light', force_send=True)
                    if self.env.company.is_notify_to_user_vendor and self.env.company.sh_user_ids_vendor:
                        url = ''
                        base_url = request.env['ir.config_parameter'].sudo(
                        ).get_param('web.base.url')
                        url = base_url + "/web#id=" + \
                              str(record.id) + \
                              "&&model=pdc.wizard&view_type=form&view_id=" + str(view_id)
                        ctx = {
                            "customer_url": url,
                        }
                        template_download_id = record.env['ir.model.data'].get_object(
                            'sh_pdc', 'sh_pdc_company_to_int_user_notification_1'
                        )
                        _ = request.env['mail.template'].sudo().browse(template_download_id.id).with_context(
                            ctx).send_mail(
                            record.id, email_values=email_values, notif_layout='mail.mail_notification_light',
                            force_send=True)

    # Multi Action Starts for change the state of PDC check

    def action_state_register(self):
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if len(active_ids) > 0:
            active_models = self.env[active_model].browse(active_ids)
            states = active_models.mapped('state')

            if len(set(states)) == 1:
                if states[0] == 'draft':
                    for active_model in active_models:
                        active_model.action_register()
                else:
                    raise UserError(
                        "Only Draft state PDC check can switch to Register state!!")
            else:
                raise UserError(
                    "States must be same!!")

    def action_state_return(self):
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if len(active_ids) > 0:
            active_models = self.env[active_model].browse(active_ids)
            states = active_models.mapped('state')

            if len(set(states)) == 1:
                if states[0] == 'registered':
                    for active_model in active_models:
                        active_model.action_returned()
                else:
                    raise UserError(
                        "Only Register state PDC check can switch to return state!!")
            else:
                raise UserError(
                    "States must be same!!")

    def action_state_deposit(self):
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if len(active_ids) > 0:
            active_models = self.env[active_model].browse(active_ids)
            states = active_models.mapped('state')

            if len(set(states)) == 1:
                if states[0] in ['registered', 'returned', 'bounced']:
                    for active_model in active_models:
                        active_model.action_deposited()
                else:
                    raise UserError(
                        "Only Register,Return and Bounce state PDC check can switch to Deposit state!!")
            else:
                raise UserError(
                    "States must be same!!")

    def action_state_bounce(self):
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if len(active_ids) > 0:
            active_models = self.env[active_model].browse(active_ids)
            states = active_models.mapped('state')

            if len(set(states)) == 1:
                if states[0] == 'deposited':
                    for active_model in active_models:
                        active_model.action_bounced()
                else:
                    raise UserError(
                        "Only Deposit state PDC check can switch to Bounce state!!")
            else:
                raise UserError(
                    "States must be same!!")

    def action_state_done(self):
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if len(active_ids) > 0:
            active_models = self.env[active_model].browse(active_ids)
            states = active_models.mapped('state')

            if len(set(states)) == 1:
                if states[0] == 'deposited':
                    for active_model in active_models:
                        active_model.action_done()
                else:
                    raise UserError(
                        "Only Deposit state PDC check can switch to Done state!!")
            else:
                raise UserError(
                    "States must be same!!")

    def action_state_cancel(self):
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if len(active_ids) > 0:
            active_models = self.env[active_model].browse(active_ids)
            states = active_models.mapped('state')

            if len(set(states)) == 1:
                if states[0] in ['registered', 'returned', 'bounced']:
                    for active_model in active_models:
                        active_model.action_cancel()
                else:
                    raise UserError(
                        "Only Register,Return and Bounce state PDC check can switch to Cancel state!!")
            else:
                raise UserError(
                    "States must be same!!")
