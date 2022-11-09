# -*- coding: utf-8 -*-
{
    'name': "Dynamic Approval All in One",

    'summary': """
        The most configurable dynamic approval app in Odoo, can be used for all default modules and third party modules""",

    'description': """
        Configurable dynamic approval process all in one for selected model or form in all odoo modules including
        custom module / third party modules.
    """,

    'author': "Nama Integrated Solutions LLC",
    'website': "www.namais.ae",
    'support': "www.namais.ae",
    'category': 'Tools',
    'version': '15.0.1.0.0',
    'sequence': 0,
    "auto_install": False,
    "installable": True,
    "application": True,
    "license": "OPL-1",
    "images": [
        'static/description/banner.gif'
    ],

    "price": 57.31,
    "currency": "EUR",

    # any module necessary for this one to work correctly
    'depends': [
        'base',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/dynamic_approval.xml',
        'views/dynamic_approval_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
