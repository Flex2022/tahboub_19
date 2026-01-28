# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    restrict_pricelist = fields.Boolean(compute='_compute_allowed_pricelists')
    allowed_pricelists = fields.Many2many('product.pricelist', compute='_compute_allowed_pricelists')
    pricelist_id = fields.Many2one('product.pricelist', domain="[('id', 'in', allowed_pricelists)]")

    # @api.model
    # def default_get(self, fields_list):
    #     res = super(SaleOrder, self).default_get(fields_list)
    #     if any(f in fields_list for f in ['restrict_pricelist', 'allowed_pricelists']):
    #         if self.env.user.restrict_pricelist:
    #             res['restrict_pricelist'] = True
    #             res['allowed_pricelists'] = self.env.user.allowed_pricelists.filtered(
    #                 lambda pl: not pl.company_id or pl.company_id == self.company_id)
    #         else:
    #             res['restrict_pricelist'] = False
    #             res['allowed_pricelists'] = self.env['product.pricelist'].search(
    #                 [('company_id', 'in', [False, self.company_id.id])])
    #     return res

    @api.depends_context('uid')
    @api.depends('company_id')
    def _compute_allowed_pricelists(self):
        for rec in self:
            if self.env.user.restrict_pricelist:
                rec.restrict_pricelist = True
                rec.allowed_pricelists = self.env.user.allowed_pricelists.filtered(
                    lambda pl: not pl.company_id or pl.company_id == rec.company_id)
            else:
                rec.restrict_pricelist = False
                rec.allowed_pricelists = self.env['product.pricelist'].search(
                    [('company_id', 'in', [False, rec.company_id.id])])

    @api.onchange('pricelist_id')
    def onchange_pricelist_id_check_if_allowed(self):
        if self.env.user.restrict_pricelist and self.pricelist_id not in self.env.user.allowed_pricelists:
            self.pricelist_id = False


