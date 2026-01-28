# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SetDiscount(models.TransientModel):
    _name = "set.discount"
    _description = 'Set Discount'

    sale_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    discount = fields.Float(string='Name', required=True)
    category = fields.Selection([('wood', 'Wood'),
                                 ('bedroom', 'Bedroom'),
                                 ('accessory', 'Accessories'),
                                 ('mixer', 'Sinks & Mixers'),
                                 ('electronic', 'Electromechanical Work'),
                                 ('worktop', 'Worktops'),
                                 ('service', 'Services'),
                                 ('appliance', 'Electric Hardware'),
                                 ], string='Category', required=True)

    def get_discount_value(self):
        '''
        This function because we are using widget="percentage" in xml
        :return: float (discount percentage)
        '''
        return self.discount * 100

    @api.constrains('discount')
    def check_discount(self):
        if self.filtered(lambda w: w.discount < 0):
            raise ValidationError(_('Discount should be positive.'))

    def action_confirm(self):
        discount = self.get_discount_value()
        if self.category == 'wood':
            self.sale_id.wood_order_line.write({'discount': discount})
        if self.category == 'bedroom':
            self.sale_id.bedroom_order_line.write({'discount': discount})
        if self.category == 'accessory':
            self.sale_id.accessory_order_line.write({'discount': discount})
        if self.category == 'mixer':
            self.sale_id.mixer_order_line.write({'discount': discount})
        if self.category == 'electronic':
            self.sale_id.electronic_order_line.write({'discount': discount})
        if self.category == 'worktop':
            self.sale_id.worktop_order_line.write({'discount': discount})
        if self.category == 'service':
            self.sale_id.service_order_line.write({'discount': discount})
        if self.category == 'appliance':
            self.sale_id.appliance_order_line.write({'discount': discount})

