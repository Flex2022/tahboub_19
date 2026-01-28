from odoo import fields, models


class PDCActualDateWizard(models.TransientModel):
    _name = 'pdc.actual.date.wizard'
    _description = 'PDC Actual Date Wizard'

    sh_pdc_id = fields.Many2one('pdc.wizard', string="PDC Wizard")
    actual_date = fields.Date(string="Actual Date", required=True)

    def action_done(self):
        self.sh_pdc_id.actual_date = self.actual_date
        self.sh_pdc_id.action_done()
