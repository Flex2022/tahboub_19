# -*- coding: utf-8 -*-
{
    'name': "Sales Workflow",
    'description': """
    - Pre-Confirm state in sale orders
    """,
    'summary': "",
    'version': '19.0.1',
    'author': "Hossam Zaki - Flex-Ops",
    'website': "https://flex-ops.com",
    'category': '',
    'license': 'OPL-1',
    'depends': ['base',
                'sale',
                'account',
                'mrp',
                'hz_sale_custom',
                'flex_mrp_custom',
                'industry_fsm_sale',
                ],
    'data': [
        'security/groups.xml',
        'views/sale.xml',
        'views/stock_quant.xml',
        'views/stock_picking.xml',
        'views/account_move.xml',
        'views/settings.xml',
        'views/product_views.xml',
        'reports/sale.xml',
        'reports/delivery_list.xml',
    ],
    'installable': True,
    'application': False,
}