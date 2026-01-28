from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.depends('account_move_id')
    def move_count_from_task(self):
        self.move_count = len(self.account_move_id)

    account_move_id = fields.Many2one('account.move')
    move_count = fields.Integer(compute="move_count_from_task", string="Move Count")

    def check_if_not_service_product(self):
        if all(p.product_id.type == 'service' for p in self.sale_order_id.order_line):
            return True

    # def create_invoice(self):
    #     # create product with sale order item in timesheet_ids if not exist
    #
    #     for line in self.timesheet_ids:
    #         if not self.env['product.product'].search([('name', '=', line.so_line.display_name)]):
    #             product = self.env['product.product'].create({
    #                 'name': line.so_line.display_name,
    #                 'type': 'service',
    #                 'task_qty': line.unit_amount,
    #                 'standard_price': line.so_line.price_unit,
    #             })
    #             line.product_id = product.id
    #
    #     for line in self.timesheet_ids:
    #         invoice = self.env['account.move'].create({
    #             'move_type': 'in_invoice',
    #             'date': fields.Date.today(),
    #             'invoice_date': fields.Date.today(),
    #             'state': 'draft',
    #             'invoice_line_ids': [(0, 0, {'product_id': line.so_line.id, 'price_unit': line.so_line.price_unit,
    #                                          'quantity': line.unit_amount})]
    #         })
    #         self.account_move_id = invoice
    def create_invoice(self):
        product_dict = {}  # Dictionary to store created product references

        for line in self.timesheet_ids:
            # Check if the product already exists or has been created in this session
            product_name = line.so_line.display_name
            product = self.env['product.product'].search([('name', '=', product_name)], limit=1)

            if not product:
                # Create the product if it does not exist
                product = self.env['product.product'].create({
                    'name': product_name,
                    'type': 'service',
                    'task_qty': line.unit_amount,
                    'standard_price': line.so_line.price_unit,
                })

            # Store the product reference in the dictionary
            product_dict[product_name] = product
            # Assign the created product ID to the timesheet line
            line.product_id = product.id

        # Create the invoice with the collected timesheet lines
        invoice_lines = []
        for rec in self:
            for line in rec.timesheet_ids:
                product = product_dict[line.so_line.display_name]
                invoice_line = {
                    'product_id': product.id,
                    'price_unit': line.so_line.price_unit,
                    'quantity': line.unit_amount,
                    'analytic_account_id': rec.analytic_account_id.id,
                }
                invoice_lines.append((0, 0, invoice_line))

        invoice = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'date': fields.Date.today(),
            'invoice_date': fields.Date.today(),
            'state': 'draft',
            'invoice_line_ids': invoice_lines
        })
        self.account_move_id = invoice

    def action_view_invoice(self):
        if self.account_move_id:
            return {
                'view_mode': 'form',
                'res_id': self.account_move_id.id,
                'res_model': 'account.move',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
            }


class ProductProduct(models.Model):
    _inherit = 'product.product'

    task_qty = fields.Float(string='Task Quantity')
