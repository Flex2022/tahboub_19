{
    'name': 'Flex Payment Tax',
    'version': '19.0.0.1',
    'summary': 'Tax with entry for payments',
    'description': '''
    - Tax with entry for payments
    - Reversal tax entry when reconcile
    - Synchronize tax from payment to entry
    ''',
    'category': 'Accounting/Accounting',
    'author': "Hossam Zaki - Flex-Ops",
    'website': "https://flex-ops.com",
    'depends': ['base', 'account'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/account_payment.xml',
        'views/res_config_settings.xml',
        # wizards
        'wizards/payment_register.xml',
        'wizards/add_payment_tax.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
