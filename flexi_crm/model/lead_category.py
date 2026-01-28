from odoo import models, api, fields, _
from odoo.exceptions import UserError


class LeadCategory(models.Model):
    _name = 'lead.category'
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string='Sequence')
