{
    'name': 'Jordan E-Invoice Integration',
    'summary': """ISTD Jordan E-Invoice Integration""",
    'version': '19.0',
    'description': 'This module integrate odoo with jordan ISTD to send invoices',
    'live_test_url': 'https://www.youtube.com/watch?v=7lLL8eSl6l4',
    'category': '',
    'author': "Flex-Ops - Abdalrahman Shahrour",
    'website': "https://flex-ops.com",
    'license': 'LGPL-3',
    'depends': ['base',
                'account',
                'contacts',
                ],
    'data': [
        # views
        'views/account_move.xml',
        'views/res_company.xml',
        'views/res_config_settings.xml',
        'views/fiscal_position.xml',
        'views/account_tax.xml',
        # 'views/configration.xml',
        # reports
        'reports/invoice.xml',

        # data
        'data/ir_cron.xml',
        'data/data.xml',
    ],
    "images": ["static/description/assets/screenshots/hero.gif",],
    "auto_install": False,
    "installable": True,
    "application": True,
    "price": 300,
    "currency": "USD"
}
