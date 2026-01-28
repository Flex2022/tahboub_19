# -*- coding: utf-8 -*-
{
    'name': "Advanced Landed Cost",
    'description': "This module allows you to add landed costs to a group of products of your choice.",
    'summary': "Add landed costs to a group of products of your choice.",
    'version': '19.0.1',
    'author': "Hossam Zaki - Flex-Ops",
    'website': "https://flex-ops.com",
    'category': '',
    'license': 'LGPL-3',
    'depends': ['base',
                'stock_landed_costs',
                ],
    'data': [
        'views/landed_cost.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}