# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    tax_id = fields.Many2one(comodel_name="account.tax", string="Tax",
                             domain=[('type_tax_use', '=', 'sale'), ('amount_type', '=', 'percent')])
    use_payment_tax = fields.Boolean(related="company_id.use_payment_tax", string="Enable Tax Entry")

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        res['tax_id'] = self.tax_id.id
        return res

    def _create_payment_vals_from_batch(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_batch(batch_result)
        res['tax_id'] = self.tax_id.id
        return res


