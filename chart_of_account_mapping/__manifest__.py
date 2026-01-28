# -*- coding: utf-8 -*-
{
    'name': "Chart Of Account Mapping",

    'summary': """
         Chart Of Account Mapping """,

    'description': """
        Chart Of Account Mapping
    """,

    'author': "Abdullah Almashaqbeh",
    'website': "+962786664713",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'mail', 'analytic'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/chart_of_account_mapping_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
