# -*- coding: utf-8 -*-
{
    'name': "Product Brand Management",
    'summary': "Manage and categorize products by their brands.",
    'description': "A module to handle product branding, including categorization, reporting, and integration with sales and stock modules.",
    'author': "Flex-Ops",
    'website': "https://flex-ops.com",
    'version': '19.0.0.1',
    'depends': ['sale', 'stock_account', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/brand_view.xml',
        'views/product_template_inherit_view.xml',
        'views/sale_order.xml',
        'views/stock.xml',
        # 'reports/sale.xml',
    ],
}
