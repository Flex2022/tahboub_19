from odoo import models, api, fields, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    warn_mobile_exist = fields.Boolean(compute='_get_warn_mobile_exist')
    mobile = fields.Char()

    @api.onchange('state_id')
    def _onchange_state_id(self):
        self.street = self.state_id.name

    @api.constrains('name')
    def _check_name_is_triple(self):
        # is_triple = self.env['ir.config_parameter'].sudo().get_param('flexi_crm.is_crm_fields_required')
        is_triple = self.env.company.is_name_triple
        # if self.env.context.get('name_is_triple'):
        if is_triple:
            if self.filtered(lambda p: p.name and len(p.name.strip().split()) < 3):
                raise UserError(_('Name should be triple.'))

    @api.constrains('mobile')
    def _check_mobile_valid(self):
        if self.filtered(lambda p: p.mobile and p.mobile.strip() and p.mobile.strip()[0] != '+'):
            raise UserError(_('Mobile should start with (+)'))

    def _get_warn_mobile_exist(self):
        for partner in self:
            partner.warn_mobile_exist = False
            if partner.mobile:
                self._cr.execute(f'SELECT count(*) FROM {self._table} WHERE mobile = %s AND id != %s',
                                 [partner.mobile, partner.id])
                count = self._cr.fetchone()[0]
                if count > 0:
                    partner.warn_mobile_exist = True

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if not recs:
            recs = self.search(['|', ('mobile', operator, name), ('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    # def _get_warn_mobile_exist(self):
    #     for partner in self:
    #         partner.warn_mobile_exist = False
    #         if partner.mobile:
    #             if self.env['res.partner'].search_count([('mobile', '=', partner.mobile), ('id', '!=', partner.id)]):
    #                 partner.warn_mobile_exist = True

    # def _check_name_is_triple(self, vals_list):
    #     for vals in vals_list:
    #         if not vals.get('name', False):
    #             continue
    #         if len(vals.get('name').strip().split()) < 3:
    #             raise UserError(_('Name should be triple.'))
    #
    # @api.model_create_multi
    # def create(self, vals_list):
    #     if self.env.context.get('name_is_triple'):
    #         self._check_name_is_triple(vals_list)
    #     return super(ResPartner, self).create(vals_list)

    @api.onchange('phone')
    def _onchange_ab_phone(self):
        if not self.phone:
            pass
        else:
            domain = [('phone', '=', self.phone)]
            if self.id.origin:
                domain.append(('id', '!=', self.id.origin))

            if self.env['res.partner'].search(domain, limit=1):
                return {'warning': {
                    'title': _("Note:"),
                    'message': _("The Phone '%s' already exists.", self.phone),
                }}
