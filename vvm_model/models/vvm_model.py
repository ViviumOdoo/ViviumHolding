# -*- coding: utf-8 -*-

from random import randint
from odoo import models, fields, api, _


class VVMModel(models.Model):
	_name = 'vvm.model'
	_description = 'VVM Model'
	_rec_name = 'model_no'

	model_no = fields.Char(string="Model No.", required=True,size=3)
	model_name = fields.Char(string="Model Name")
	model_type = fields.Char(string="Type")
	subtype = fields.Char(string="Sub-Type")
	color_ids = fields.Many2many("model.color", string="Color",	relation='vvm_model_color_rel', ondelete='restrict')
	fabric_id = fields.Many2one("vvm.model.fabric", string="Fabric")
	item_code_id = fields.Many2one("product.product", string="Item Code")
	purchase_price_eur = fields.Float(string="Purchase Price (EUR)")
	purchase_price_aed = fields.Float(string="Purchase Price (AED)")
	sale_price_aed = fields.Float(string="Sale Price (AED)")
	product_id = fields.Many2one("product.template", string="Product",copy=False)


class ModelColor(models.Model):
	_name = 'model.color'
	_description = 'Model Color'
	_sql_constraints = [
		('name', 'UNIQUE (name)', 'You can not have two color with the same name !')
	]

	def _get_default_color(self):
		return randint(1, 11)

	name = fields.Char(string="Name", required=True)
	image_1920 = fields.Image("Image")
	html_color = fields.Char(string='Color',
	help="Here you can set a specific HTML color index (e.g. #ff0000) to display the color if the attribute type is 'Color'.")
	color = fields.Integer('Color Index', default=_get_default_color)
