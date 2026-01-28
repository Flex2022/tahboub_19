# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    def action_unreserve(self):
        self = self.filtered(lambda loc: loc.usage == 'internal')
        StockMove = self.env['stock.move'].sudo()
        moves = StockMove.search([('location_id', 'in', self.ids), ('state', 'not in', ['done', 'cancel'])])
        moves._do_unreserve()

