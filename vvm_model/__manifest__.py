# -*- coding: utf-8 -*-
{
	'name': "VVM Model",

	'summary': """
		VVM Model""",

	'description': """
		VVM Model
	""",

	'author': "My Company",
	'website': "http://www.yourcompany.com",

	'category': 'Uncategorized',
	'version': '15.1',

	'depends': ['base', 'sale', 'purchase', 'stock', 'account', 'abs_hide_sale_cost_price'],

	'data': [
		'security/ir.model.access.csv',
		'data/product_storable_cron.xml',
		'views/menu_model_view.xml',
		'views/vvm_model_view.xml',
		'views/model_fabric.xml',
		'views/product.xml',
		'views/finish_category_view.xml',
		'views/sale_order_view.xml',
		'views/stock_picking_view.xml',
		'views/res_user_view.xml',
		'views/fabric_color_view.xml'
	],
	'installable': True,
	'application': True,
	'auto_install': False,
	'license': 'LGPL-3',
}
