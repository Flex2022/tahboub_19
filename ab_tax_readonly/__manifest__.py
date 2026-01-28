# -*- coding: utf-8 -*-
{
    'name': "Tax Readonly",
    'summary': "Tax Readonly",
    'description':  "Tax Readonly",
    'author': "Flex-Ops - Abdullah Almashaqbeh",
    'website': "https://flex-ops.com",
    'version': '19.0.1',
    'license': 'LGPL-3',
    'category': 'CRM',
    'depends': ['base', 'sale', 'purchase'],
    'data': [
        'security/groups.xml',
        'views/res_config_settings.xml',
        'views/ab_sale_order_line_view.xml',
        'views/ab_purchase_order_line_view.xml',
        'views/account_move.xml',
    ],
}
