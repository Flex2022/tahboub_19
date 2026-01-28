# -*- coding: utf-8 -*-
{
    'name': "Flex Manufacturing",
    'description': "",
    'summary': "",
    'version': '15.0.1',
    'author': "Hossam Zaki - Flex-Ops",
    'website': "https://flex-ops.com",
    'category': '',
    'license': 'LGPL-3',
    'depends': ['base',
                'mrp',
                'sale',
                'hz_sale_custom',
                ],
    'data': [
        'security/ir.model.access.csv',

        'views/product.xml',
        'views/mrp_production.xml',
        'reports/mrp_production.xml',

        'wizards/sale_get_product.xml',
        'wizards/import_component.xml',
    ],
    'installable': True,
    'application': False,
}