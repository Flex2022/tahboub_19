{
    'name': 'Flex Fiscal Position Domain',
    'version': '19.0.1.0.0',
    'summary': 'Restrict fiscal positions per user on sale orders',
    'author': 'Flex-ops',
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'views/res_users.xml',
        'views/sale.xml',
    ],
    'installable': True,
    'application': False,
}

