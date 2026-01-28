# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('default_code', )
    def _check_default_code(self):
        for record in self:
            template_count = self.env['product.template'].search_count([('default_code', '=', record.default_code), ('default_code', '!=', False)])
            if template_count > 1:
                raise ValidationError(_('Internal Reference (%s) already exists !' % record.default_code))

