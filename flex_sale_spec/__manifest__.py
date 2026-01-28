# -*- coding: utf-8 -*-
{
    'name': "Flex Sale Specifications.",
    'description': "",
    'summary': "",
    'version': '19.0.1',
    'author': "Hossam Zaki - Flex-Ops",
    'website': "https://flex-ops.com",
    'category': '',
    'license': 'LGPL-3',
    'depends': ['base', 'sale'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/sale_spec.xml',
        'views/sale.xml',
        'views/bedroom.xml',
        # reports
        'reports/specification_form.xml',
        'reports/bedroom_report.xml',
    ],
    'installable': True,
    'application': False,
}