from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class ImportJournalEntry(models.Model):
    _name = "import.journal.entry"

    def _get_current_company(self):
        return self.env.company.id

    unique_identification = fields.Integer('Unique Identification')
    reference = fields.Char('Reference')
    account_code = fields.Char('Account Code')
    old_account_code = fields.Char('Old Code')
    partner = fields.Char('Partner')
    label = fields.Char('Label')
    analytic_account = fields.Char('Analytic Account')
    analytic_tags = fields.Char('Analytic Tags')
    debit = fields.Float('Debit', digits=(12,3))
    credit = fields.Float('Credit', digits=(12,3))
    tax = fields.Char('Taxes')
    accounting_date = fields.Date('Accounting Date')
    # journal = fields.Char('Journal')
    state = fields.Char('State', default='Draft')
    company_id = fields.Many2one('res.company', 'Company', default=_get_current_company)
    account_move_id = fields.Many2one('account.move', 'Account Move')



    def action_create_journal_entry(self):
        ac_dict = {}
        for record in self:
            key = str(record.unique_identification)
            if key not in ac_dict:
                ac_dict[key] = [record.id]
            else:
                ac_dict[key].append(record.id)


        for line in ac_dict:
            object_line = self.env['import.journal.entry'].browse(ac_dict[line])
            object_line_with_reference = object_line.filtered(lambda lm: lm.reference != False)[0]
            object_line_without_reference = object_line.filtered(lambda lm: lm.reference == False)

            # print(object_line_with_reference.reference)

            line_ids = []
            for line in object_line:
                partner_id = False
                if line.partner:
                    partner = self.env['res.partner'].search([('name', '=', line.partner)], order='company_id', limit=1)
                    if not partner:
                        raise ValidationError(f"Partner: {line.partner} not found in the system.")
                    # if len(partner) > 1:
                    #     raise ValidationError(f"Multiple partner: {line.partner} found in the system.")
                    partner_id = partner.id
                debit_line = (0, 0, {
                    'account_id': self.env['account.account'].search([('code', '=', line.account_code)]).id,
                    'analytic_account_id': self.env['account.analytic.account'].search([('name', '=', line.analytic_account)]).id,
                    'partner_id': partner_id,
                    'name': line.label,
                    'debit': line.debit,
                    'credit': line.credit,
                })
                line_ids.append(debit_line)


            account_move_id = self.env['account.move'].create({
                'ref': object_line_with_reference.reference,
                'date': object_line_with_reference.accounting_date,
                'journal_id': self.env['account.journal'].search([('name', '=', 'Miscellaneous Operations')]).id,
                'line_ids': line_ids,
            })

            for line in object_line:
                line.state = 'Posted'
                line.account_move_id = account_move_id





