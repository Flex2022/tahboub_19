# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AddPaymentTax(models.TransientModel):
    _name = 'add.payment.tax'
    _description = 'Generate Payment Tax Entries'

    tax_id = fields.Many2one(
        comodel_name="account.tax",
        string="Tax",
        domain=[('type_tax_use', '=', 'sale'), ('amount_type', '=', 'percent')],
        required=True,
    )
    payment_ids = fields.Many2many(
        comodel_name="account.payment",
        string="Payments",
        default=lambda s: s._context.get('active_ids', []),
    )

    def generate_tax_moves(self):
        if not self.payment_ids:
            raise ValidationError(_('Please select some payments to generate tax entries'))
        not_allowed_companies = self.payment_ids.filtered(lambda pay: not pay.company_id.use_payment_tax).company_id
        if not_allowed_companies:
            raise ValidationError(_('Tax on payments is not activated for companies: [%s]')
                                  % ', '.join(not_allowed_companies.mapped('name')))
        if self.payment_ids.filtered(lambda pay: pay.state != 'posted'):
            raise ValidationError(_('You can generate tax entries for only posted payments'))
        if self.payment_ids.filtered('tax_move_id'):
            raise ValidationError(_('There are some payments already have tax entries'))
        self.payment_ids.with_context(auto_post_tax_move=True).write({'tax_id': self.tax_id.id})

