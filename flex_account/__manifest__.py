# -*- coding: utf-8 -*-
{
    'name': "Flex Accounting Features",
    'description': "",
    'summary': "",
    'version': '19.0.1',
    'author': "Hossam Zaki - Flex-Ops",
    'website': "https://flex-ops.com",
    'category': '',
    'license': 'LGPL-3',
    'depends': ['base',
                'account',
                ],
    'data': [
        'security/groups.xml',
        # 'security/ir.model.access.csv',
        'views/res_config_settings.xml',
    ],
    'installable': True,
    'application': False,
}