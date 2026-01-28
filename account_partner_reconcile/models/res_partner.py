from odoo import models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_open_reconcile(self):
        self.ensure_one()
        reconcile_mode = self.env.context.get("reconcile_mode", "customers")

        # Determine the account type based on mode
        account_type = 'asset_receivable' if reconcile_mode == 'customers' else 'liability_payable'

        return {
            'name': 'Reconcile Lines',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_mode': 'list',
            'domain': [
                ('partner_id', '=', self.id),
                ('account_id.account_type', '=', account_type),
                ('reconciled', '=', False),
                ('parent_state', '=', 'posted'),
            ],
            'context': {'search_default_unreconciled': 1},
        }