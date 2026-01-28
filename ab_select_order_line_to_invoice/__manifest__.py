# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

{
    'name': "Select Order Line To Invoice",
    'version': '19.0.1.0',
    'author': 'Abdullah Almashaqbeh',
    'summary': """Select Order Line To Invoice""",
    'description': """
     Select Order Line To Invoice
    """,
    'license': 'OPL-1',
    'depends': ['base', 'sale'],
    'website': "",
    'data': [
        'views/sale_advance_payment_inv.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

