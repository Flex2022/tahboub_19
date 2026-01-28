# -*- coding: utf-8 -*-
{
    'name': "Pricelist User Restriction",
    'description': "Restrict pricelists for specific user(s)",
    'summary': "",
    'version': '15.0.1',
    'author': "Hossam Zaki - Flex-Ops",
    'website': "https://flex-ops.com",
    'category': '',
    'license': 'LGPL-3',
    'depends': ['base',
                'product',
                'sale',
                ],
    'data': [
        'views/res_users.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'application': False,
}