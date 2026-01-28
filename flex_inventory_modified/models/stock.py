from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_address = fields.Char(string='Address', compute='_compute_partner_address', store=True)
    company_iden = fields.Char(string='Company Identifier', compute='_compute_company_iden', store=True)
    driver_name = fields.Char(string='Driver Name')


    @api.depends('company_id')
    def _compute_company_iden(self):
        for rec in self:
            if rec.company_id:
                rec.company_iden = rec.company_id.id
            else:
                rec.company_iden = ''

    @api.depends('partner_id')
    def _compute_partner_address(self):
        for rec in self:
            if rec.partner_id:
                # Create address components list, ensuring no 'False' values are displayed
                address_parts = [
                    rec.partner_id.street or '',  # Street
                    rec.partner_id.street2 or '',  # Street 2
                    rec.partner_id.city or '',  # City
                    rec.partner_id.state_id.name or '',  # State
                    rec.partner_id.zip or '',  # ZIP Code
                    rec.partner_id.country_id.name or '',  # Country
                    rec.partner_id.phone or ''  # Phone
                ]

                # Join non-empty components with a comma
                rec.partner_address = ', '.join(filter(None, address_parts))
            else:
                rec.partner_address = ''


    def _get_report_lang(self):
        return self.move_ids and self.move_ids[0].partner_id.lang or self.partner_id.lang or self.env.lang


    # def should_print_delivery_address(self):
    #     self.ensure_one()
    #     return self.move_lines and self.move_lines[0].partner_id and self._is_to_external_location()