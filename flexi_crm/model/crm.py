from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    age_cat = fields.Selection([
        ('20s', '20s'), ('30s', '30s'), ('40s', '40s'), ('50s', '50s'), ('60s<', '60s<')],
        string='Age Cat')

    budget = fields.Selection([
        ('6000-10000', '6000-10000'), ('11000-15000', '11000-15000'), ('16000-20000', '16000-20000'), ('<20000', '<20000')],
        string='Budget')

    residence_type = fields.Selection([
        ('villa', 'Villa'), ('apartment', 'Apartment'), ('company', 'Company'), ('studio', 'Studio')],
        string='Residence Type')

    residence_space = fields.Selection([
        ('300<', '300<'), ('220-300', '220-300'), ('170-220', '170-220'), ('135-170', '135-170'), ('100-135', '100-135')],
        string='Residence Space')

    place_residence = fields.Selection([
        ('jordan', 'Jordan'), ('gulf', 'Gulf'), ('europe', 'Europe'), ('america', 'America'),
        ('australia', 'Australia'), ('far_east', 'Far East')],
        string='Place Type')

    product_categ_id = fields.Many2one('product.category', string='Product Category')
    is_name_triple = fields.Boolean(string='CRM Fields Required?', related='company_id.is_name_triple')
    lead_categ_id = fields.Many2one('lead.category', string='Project Category', ondelete='restrict')

    # Computed boolean for required fields
    @api.depends('company_id')
    def _compute_required_fields(self):
        for lead in self:
            company = lead.company_id
            lead._required_fields = [(f.name.name if f.name else False) for f in company.ab_required_fields_ids]

    _required_fields = fields.Char(compute='_compute_required_fields')


class RequiredFields(models.Model):
    _name = 'ab.required.fields'
    _description = 'Required CRM Fields per Company'

    name = fields.Many2one('ir.model.fields', string='Field', domain="[('model', '=', 'crm.lead')]")
    res_company_id = fields.Many2one('res.company', string='Company')
