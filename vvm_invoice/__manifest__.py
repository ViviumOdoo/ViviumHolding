# -*- coding: utf-8 -*-
{
    'name': "VVM Reporting",

    'summary': """
        VVM Reporting""",

    'description': """
        VVM Reporting
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.15.1',

    'depends': ['base', 'account', 'sale', 'account_asset'],

    'data': [
        'data/data.xml',
        'views/report_invoice.xml',
        'views/account_move_view.xml',
        'views/account_asset_view.xml'
    ]
}
