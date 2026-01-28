# -*- coding: utf-8 -*-
{
    'name': "Flex Purchase Features",
    'description': """
    - Barcode in purchase order line
    - Print barcode in purchase pdf report""",
    'summary': "",
    'version': '19.0.1',
    'author': "Hossam Zaki - Flex-Ops",
    'website': "https://flex-ops.com",
    'category': '',
    'license': 'LGPL-3',
    'depends': ['base',
                'purchase',
                ],
    'data': [
        'views/purchase_order.xml',
        'reports/purchase.xml',
    ],
    'installable': True,
    'application': False,
}