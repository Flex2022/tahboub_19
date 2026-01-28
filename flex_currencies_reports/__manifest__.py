# -*- coding: utf-8 -*-
{
    'name': "Currencies Reports",

    'summary': """
        Currencies Reports""",

    'description': """
        Add an other currency with this rate to print it in the report..
    """,
    'author': "HACHEMI Mohamed Ramzi",
    'website': "https://flex-ops.com",
    'category': '',
    'license': 'LGPL-3',
    'sequence': 192,
    'version': '19.0.0.1',
    'depends': ['base', 'sale', 'sale_management', 'purchase', 'account'],


    'data': [
        # 'security/ir.model.access.csv',
        # 'data/data.xml',
        'security/security.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/account_move.xml',
        # 'reports/sale_order_report.xml',
        # 'reports/purchase_order_report.xml',
        # 'reports/account_move_report.xml',
    ],
}
