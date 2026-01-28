# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class CustomerProject(models.Model):
    _name = 'customer.project'
    _description = 'Customer Project'

    name = fields.Char(string='Name', required=True)
