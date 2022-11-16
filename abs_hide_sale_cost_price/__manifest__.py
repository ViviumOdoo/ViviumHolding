# -*- coding: utf-8 -*-

{
    'name': "Hide Sale and Cost Price of the Product",
    'author': 'Nama Integrate Solution LLC',
    'category': 'Sales',
    'summary': """Hide Sale and Cost Price of the Product""",
    'website': 'http://www.nama.ae',
    'description': """Hide Sale and Cost Price of the Product""",
    'version': '15.0.1.0',
    'depends': ['base','sale_management','product'],
    'data': ['security/show_sale_cost_price_fields.xml', 'views/view_sale_cost_price_product.xml'
           ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',    
    'installable': True,
    'application': True,
    'auto_install': False,
}
