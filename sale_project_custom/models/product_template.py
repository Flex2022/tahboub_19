from odoo import fields, models, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Override Method [contain type of product [storable product]]
    @api.depends('service_tracking', 'type')
    def _compute_product_tooltip(self):
        res = super(ProductTemplate, self)._compute_product_tooltip()
        super()._compute_product_tooltip()
        for record in self.filtered(lambda record: record.type in ['service','product']):
            if record.service_tracking == 'no':
                record.product_tooltip = _(
                    "Invoice ordered quantities as soon as this service is sold."
                )
            elif record.service_tracking == 'task_global_project':
                record.product_tooltip = _(
                    "Invoice as soon as this service is sold, and create a task in an existing "
                    "project to track the time spent."
                )
            elif record.service_tracking == 'task_in_project':
                record.product_tooltip = _(
                    "Invoice ordered quantities as soon as this service is sold, and create a "
                    "project for the order with a task for each sales order line to track the time"
                    " spent."
                )
            elif record.service_tracking == 'project_only':
                record.product_tooltip = _(
                    "Invoice ordered quantities as soon as this service is sold, and create an "
                    "empty project for the order to track the time spent."
                )
        return res

    # Override Method [contain type of product [storable product]]
    @api.onchange('type')
    def _onchange_type(self):
        res = super(ProductTemplate, self)._onchange_type()
        if self.type not in ['service','product']:
            self.service_tracking = 'no'
        return res




