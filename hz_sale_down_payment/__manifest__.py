# -*- coding: utf-8 -*-
{
    'name': "Sale Down Payment",
    'description': "Customizing down payments on sale orders",
    'summary': "",
    'version': '19.0.1',
    'author': "Hossam Zaki - Flex-Ops",
    'website': "https://flex-ops.com",
    'category': '',
    'license': 'LGPL-3',
    'depends': ['base',
                'sale',
                'sales_team',
                'account',
                'bi_sale_advance_payment',
                ],
    'data': [
        'security/ir.model.access.csv',

        'views/res_users.xml',
        'views/sale_order.xml',

        'wizard/invoice_advance.xml',
        'wizard/bi_advance_payment.xml',
    ],
    'installable': True,
    'application': False,
}