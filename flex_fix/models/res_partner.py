# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_sale_record_ids(self, p_id, field_name):
        self._cr.execute(f"SELECT id FROM sale_order WHERE {field_name} = {p_id}")
        return [r[0] for r in self._cr.fetchall()]

    def _update_sale_record_ids(self, record_ids, new_id, field_name):
        self._cr.execute(f"""UPDATE sale_order 
                SET {field_name}={new_id} 
                WHERE id IN %s""", [tuple(record_ids)])

    def _get_record_ids(self, p_id, table):
        self._cr.execute(f"SELECT id FROM {table} WHERE partner_id = {p_id}")
        return [r[0] for r in self._cr.fetchall()]

    def _update_record_ids(self, record_ids, new_id, table):
        self._cr.execute(f"""UPDATE {table} 
        SET partner_id={new_id} 
        {f', partner_invoice_id={new_id}, partner_shipping_id={new_id}' if table=='sale_order' else ''} 
        {f', commercial_partner_id={new_id}, partner_shipping_id={new_id}' if table=='account_move' else ''} 
        WHERE id IN %s""", [tuple(record_ids)])

    @api.model
    def action_fix_duplicate(self):
        # self._cr.execute("""
        #    SELECT p1.id AS ID, p2.num
        #    FROM res_partner p1
        #    JOIN (SELECT name, COUNT(id) AS num FROM res_partner GROUP BY name HAVING COUNT(id) > 1) p2 ON p1.name = p2.name ORDER BY p1.name;
        #    """)
        self._cr.execute("""
           SELECT p1.name AS name, p1.id AS id
           FROM res_partner p1 
           JOIN (SELECT name, COUNT(id) AS num FROM res_partner GROUP BY name HAVING COUNT(id) > 1) p2 ON p1.name = p2.name ORDER BY p1.company_id;
           """)
        res = self._cr.fetchall()
        result = {}
        if res:
            for r in res:
                result.setdefault(r[0], [])
                result[r[0]] += [r[1]]

        tables_to_check = ['account_move',
                           'account_move_line',
                           'purchase_order',
                           'sale_order',
                           'crm_lead',
                           'account_payment',
                           'stock_picking',
                           'repair_order',
                           'account_payment_register',
                           'calendar_attendee',
                           ]
        to_delete = []
        for partner_group_ids in list(result.values())[-100:]:
            for p_id in partner_group_ids[1:]:
                for table in tables_to_check:
                    record_ids = self._get_record_ids(p_id, table)
                    if record_ids:
                        self._update_record_ids(record_ids, partner_group_ids[0], table)
                sale_record_ids = self._get_sale_record_ids(p_id, 'partner_invoice_id')
                if sale_record_ids:
                    self._update_sale_record_ids(sale_record_ids, partner_group_ids[0], 'partner_invoice_id')
                sale_record_ids = self._get_sale_record_ids(p_id, 'partner_shipping_id')
                if sale_record_ids:
                    self._update_sale_record_ids(sale_record_ids, partner_group_ids[0], 'partner_shipping_id')
                to_delete += [p_id]
        self.env['res.partner'].sudo().browse(to_delete).unlink()
        print(f"{len(to_delete)} partners removed")


        # p_ids = []
        # for g in list(result.values())[:]:
        #     p_ids += [id for id in g]
        # print(p_ids)
        # return {
        #     'name': _('Duplicated'),
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'res.partner',
        #     'view_mode': 'tree,form',
        #     'domain': [('id', 'in', p_ids[:50])],
        # }

    # def get_number_of_repeatitions(self):
    #     self._cr.execute("""
    #         SELECT p2.num, Count(p1.*)
    #         FROM res_partner p1
    #             JOIN (SELECT name, COUNT(id) AS num FROM res_partner GROUP BY name HAVING COUNT(id) > 1) p2 ON p1.name = p2.name
    #         GROUP BY p2.num;
    #        """)
