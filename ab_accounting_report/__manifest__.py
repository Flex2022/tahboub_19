# -*- coding: utf-8 -*-
{
    'name': "Tahboub Accounting Report Customization",
    'description': "Tahboub Accounting Report Customization",
    'summary': "Tahboub Accounting Report Customization",
    'version': '19.0.0.1',
    'author': "Abdullah Almashaqbeh - Flex-Ops",
    'website': "https://flex-ops.com",
    'category': '',
    'license': 'LGPL-3',
    'depends': ['base',
                'sale',
                'account',
                'brand'],
    'data': [
        'reports/invoice_customization.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}