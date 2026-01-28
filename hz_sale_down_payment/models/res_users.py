# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    restrict_journals = fields.Boolean(string='Journal Restriction In SO Advance Payments')
    allowed_journals = fields.Many2many(
        'account.journal', 'user_allowed_journal', string='Allowed Journals', copy=False)
