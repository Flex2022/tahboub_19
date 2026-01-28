# -*- coding: utf-8 -*-
from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    code_l10n_jo = fields.Char(string='Code', help='Code In ISTD Portal')


    l10n_jo_tax_company_type = fields.Selection(
        string='Tax Company Type', help="The type of the company for tax purposes.",
        selection=[
            ('1', 'Income'),
            ('2', 'sales'),
            ('3', 'Privet'),
        ])


    # @api.model
    # def _process_end_unlink_record(self, record):
    #     try:
    #         for field in self._fields.values():
    #             if isinstance(field, (fields.Many2one, fields.One2many, fields.Many2many)):
    #                 ondelete = (field.ondelete or {}).get(record.some_field)
    #                 _logger.debug(f"Processing ondelete action for field: {field.name} with value: {ondelete}")
    #     except Exception as e:
    #         _logger.error(f"Error processing end unlink record: {e}")
