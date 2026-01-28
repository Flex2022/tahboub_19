from odoo.exceptions import ValidationError
from odoo import api, fields, models, _


class SelectPaymentWizard(models.TransientModel):
    _name = 'select.payment.wizard'
    _description = 'Select Payment Wizard'

    account_payment_ids = fields.Many2many('account.payment', 'select_payment_wiz_rel', string='Account Payment')

    # @api.onchange('account_payment_ids')
    # def _onchange_account_payment_ids(self):
    #     sale_order_id = self.env['sale.order'].browse(self.env.context.get('active_id'))
    #     domain = [('partner_id', '=', sale_order_id.partner_id.id),
    #               ('payment_type', '=', 'inbound'),
    #               ('id', 'not in', sale_order_id.account_payment_ids.ids),
    #               ('company_id', '=', sale_order_id.company_id.id),
    #               ('remaining', '>', 0)]
    #     if sale_order_id.partner_id:
    #         self._cr.execute(f"""
    #         SELECT tb.payment_id
    #             FROM (
    #                 SELECT ap.id AS payment_id, ap.amount AS payment_amount, sum(so.amount_untaxed) AS total_sales
    #                     FROM sale_payment_rel AS spr
    #                     JOIN sale_order AS so ON (so.id=spr.sale_order_id)
    #                     JOIN account_payment AS ap ON (ap.id=spr.account_payment_id)
    #                     WHERE ap.partner_id={sale_order_id.partner_id.id}
    #                     GROUP BY ap.id
    #             ) AS tb
    #         WHERE tb.payment_amount <= tb.total_sales+{sale_order_id.amount_untaxed};
    #         """)
    #         domain += [('state', '=', 'posted'), ('id', 'not in', [r[0] for r in self._cr.fetchall()])]
    #     return {'domain': {'account_payment_ids': domain}}

    @api.onchange('account_payment_ids')
    def _onchange_account_payment_ids(self):
        sale_order_id = self.env['sale.order'].browse(self.env.context.get('active_id'))
        company = sale_order_id.company_id
        partner = sale_order_id.partner_id
        domain = [('partner_id', '=', partner.id),
                  ('payment_type', '=', 'inbound'),
                  ('id', 'not in', sale_order_id.account_payment_ids.ids),
                  ('company_id', '=', company.id),
                  ('remaining', '>', 0),
                  ('state', '=', 'posted')]
        percent = partner.sale_advance_payment_percent if partner.sale_advance_payment_percent > 0 else company.sale_advance_payment_percent
        percent *= 0.01
        if percent > 0:
            self._cr.execute(f"""
            SELECT tb.payment_id 
                FROM (
                    SELECT ap.id AS payment_id, ap.amount AS payment_amount, sum(so.amount_total) AS total_sales, {percent} * sum(so.amount_total) as payment_reserved_amount
                        FROM sale_payment_rel AS spr
                        JOIN sale_order AS so ON (so.id=spr.sale_order_id) 
                        JOIN account_payment AS ap ON (ap.id=spr.account_payment_id) 
                        WHERE ap.partner_id={partner.id} and so.state not in ('cancel')
                        GROUP BY ap.id
                ) AS tb
            WHERE tb.payment_amount <= tb.payment_reserved_amount + ({percent * sale_order_id.amount_total});
            """)
            domain += [('id', 'not in', [r[0] for r in self._cr.fetchall()])]
        return {'domain': {'account_payment_ids': domain}}

    def action_get_payments(self):
        sale_order_id = self.env['sale.order'].browse(self.env.context.get('active_id'))
        exist_payment_ids = sale_order_id.account_payment_ids.ids
        new_payment_ids = self.account_payment_ids.ids
        for id in new_payment_ids:
            if id not in exist_payment_ids:
                exist_payment_ids.append(id)
        sale_order_id.account_payment_ids = exist_payment_ids
