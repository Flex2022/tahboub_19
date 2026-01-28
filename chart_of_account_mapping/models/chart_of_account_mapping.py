from odoo import fields, models, api,_

class ChartOfAccountMapping(models.Model):
    _name = 'chart.of.account.mapping'

    code_old = fields.Char(string='Code-Old',)
    account_name_old = fields.Char('Account Name-Old',)
    account_account_id = fields.Many2one('account.account', string='Account',)
    partner_id = fields.Many2one('res.partner', string='Partner',)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',)
    company_id = fields.Many2one('res.company', string="Company")