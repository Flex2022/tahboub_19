# -*- coding: utf-8 -*-
{
    'name': "Sales Discount Per Category.",
    'description': """
    - Discount limit per category for each user
    """,
    'summary': "",
    'version': '19.0.1',
    'author': "Hossam Zaki - Flex-Ops",
    'website': "https://flex-ops.com",
    'category': '',
    'license': 'LGPL-3',
    'depends': ['base',
                'hz_sale_custom',
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users.xml',
        'views/sale.xml',
    ],
    'installable': True,
    'application': False,
}