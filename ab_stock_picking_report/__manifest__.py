# -*- coding: utf-8 -*-
{
    'name': "Tahboub Stock Picking Report Customization",
    'description': "Tahboub Stock Picking Report Customization",
    'summary': "Tahboub Stock Picking Report Customization",
    'version': '19.0.1',
    'author': "Abdullah Almashaqbeh - Flex-Ops",
    'website': "https://flex-ops.com",
    'category': '',
    'license': 'LGPL-3',
    'depends': ['base',
                'sale',
                'stock',
                'sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/ab_res_config_setting_view.xml',
        'views/ab_stock_picking_view.xml',
        'reports/delivery_slip_customization.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}