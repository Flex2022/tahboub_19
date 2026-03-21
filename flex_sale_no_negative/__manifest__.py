# -*- coding: utf-8 -*-
{
    'name': "Sales Disable Negative Stock",
    'description': """
    - Prevent negative stock in sale orders
    """,
    'summary': "",
    'version': '19.0.1.0.0',
    'author': "Hossam Zaki - Flex-Ops",
    'website': "https://flex-ops.com",
    'category': '',
    'license': 'OPL-1',
    'depends': ['base',
                'sale_stock',
                'eq_so_multi_warehouse',
                ],
    'data': [
        'security/groups.xml',
        'views/product_template.xml',
    ],
    'installable': True,
    'application': False,
}