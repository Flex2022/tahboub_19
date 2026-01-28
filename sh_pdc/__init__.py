# Copyright (C) Softhealer Technologies.

from . import models
from . import wizard

from odoo import api, SUPERUSER_ID


# TODO: Apply proper fix & remove in master


# def post_init_hook(cr, registry):
#     # Update old customers and vendors.
#     query = "UPDATE res_company SET pdc_customer=(select id from account_account where name ilike 'PDC Receivable'); " \
#             "UPDATE res_company SET pdc_vendor=(select id from account_account where name ilike 'PDC Payable');"
#     cr.execute(query)


def post_init_hook(cr, registry):
    # Using the registry to get the model's environment
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Search for the account with name 'PDC Receivable'
    pdc_receivable_account = env['account.account'].search([('name', 'ilike', 'PDC Receivable')], limit=1)

    # Search for the account with name 'PDC Payable'
    pdc_payable_account = env['account.account'].search([('name', 'ilike', 'PDC Payable')], limit=1)

    # Update the res_company fields if the accounts are found
    if pdc_receivable_account:
        env['res.company'].search([]).write({'pdc_customer': pdc_receivable_account.id})

    if pdc_payable_account:
        env['res.company'].search([]).write({'pdc_vendor': pdc_payable_account.id})
