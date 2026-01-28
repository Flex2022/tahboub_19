# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


categ_types = [('wood', 'Wood'), ('bedroom', 'Bedroom'), ('accessory', 'Accessories'),
               ('mixer', 'Sinks & Mixers'), ('electronic', 'Electromechanical Work'),
               ('worktop', 'Worktops'), ('service', 'Services'), ('appliance', 'Electric Hardware')]


class ResUsers(models.Model):
    _inherit = "res.users"

    def _default_discount_lines(self):
        return [(0, 0, {'categ_type': typ[0], 'limit': 1, 'is_enabled': True, }) for typ in categ_types]

    restrict_general_discount = fields.Boolean(string='Restrict General Discount')
    general_discount_limit = fields.Float(string='Discount Limit %')
    restrict_category_discount = fields.Boolean(string='Restrict Discount Per Category', copy=False)
    discount_line = fields.One2many('discount.line', 'user_id', string='Discount Lines', copy=False,
                                    default=_default_discount_lines)

    @api.constrains('restrict_general_discount', 'restrict_category_discount')
    def _check_discount_restriction(self):
        if self.filtered(lambda u: u.restrict_general_discount and u.restrict_category_discount):
            raise ValidationError(_('You can activate general discount or category discount, not both!'))

    @api.constrains('discount_line', 'restrict_category_discount')
    def _check_violation_line(self):
        for rec in self:
            if not rec.restrict_category_discount:
                continue
            for line in rec.discount_line:
                if rec.discount_line.filtered(lambda l: l.categ_type == line.categ_type and l.id != line.id):
                    raise ValidationError(_('The same category cannot be repeated in discount lines.'))
            if any((categ[0] not in rec.discount_line.mapped('categ_type')) for categ in categ_types):
                raise ValidationError(_('You have to set rule for each category.'))

    @api.onchange('restrict_category_discount')
    def add_discount_lines_if_not_exist(self):
        if self.restrict_category_discount and not self.discount_line:
            self.discount_line = self._default_discount_lines()

    def get_categ_discount_limit(self, categ=''):
        if self.restrict_category_discount:
            target_line = self.discount_line.filtered(lambda l: l.categ_type == categ and l.is_enabled)
            if target_line:
                return target_line[:1].limit * 100  # *100 because limit field has widget="percentage"
        return False


class DiscountLine(models.Model):
    _name = 'discount.line'
    _description = 'Discount Line'

    categ_type = fields.Selection(selection=categ_types, string='Category', required=True)
    limit = fields.Float(string='Limit', required=True, default=1)
    is_enabled = fields.Boolean(string='Enabled', default=True)
    user_id = fields.Many2one(comodel_name='res.users', string='User', ondelete='cascade', required=True)

    @api.constrains('limit')
    def _check_violation_line(self):
        # limit is (1) because we will use widget="percentage" in xml
        if self.filtered(lambda l: l.limit < 0 or l.limit > 1):
            raise ValidationError(_('The limit should be between 0  and 100'))

    def name_get(self):
        return [(line.id, f"{line.user_id.name}-{line.categ_type}") for line in self]
