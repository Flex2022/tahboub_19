# -*- coding: utf-8 -*-
{
    'name': " FlexOps - CRM",
    'summary': "FlexOps CRM",
    'description':  "FlexOps CRM",
    'author': "Flex-Ops",
    'website': "https://flex-ops.com",
    'version': '19.0.1',
    'license': 'LGPL-3',
    'category': 'CRM',
    'depends': ['crm', 'product', 'sale_crm'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/crm.xml',
        'views/res_config_settings.xml',
        'views/res_partner.xml',
        'views/res_company_view.xml',
        'views/sale.xml',
        'views/lead_category.xml',

    ],
}
