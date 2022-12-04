# -*- coding:utf-8 -*-
{
    'name': 'Qweb Report',
    'version': '15.0.0.0.0',
    'license': 'AGPL-3',
    'depends': ['sale_management', 'purchase'],
    'data': [
        'report/purchase_order_report.xml',
        'report/purchase_order_template.xml',
        'report/quotation_report.xml',
        'report/quotation_template.xml',
    ],
    'installable': True,
}