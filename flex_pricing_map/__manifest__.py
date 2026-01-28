# -*- coding: utf-8 -*-
{
    'name': "Flex Pricing Map",
    'description': """
    - Map sales prices in sale orders
    """,
    "version": "19.0.1",
    'author': "Hossam Zaki, Flex-Ops",
    'website': "https://flex-ops.com",
    "license": "OPL-1",
    'price': 60.0,
    'currency': 'EUR',
    'depends': ['sale', 'hz_sale_custom'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/price_map.xml',
        'views/sale_order.xml',
        'views/res_config_settings.xml',
        'views/menus.xml',
    ],
}
