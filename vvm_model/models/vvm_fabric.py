# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VVMFabric(models.Model):
	_name = 'vvm.model.fabric'
	_description = 'VVM Fabric'
	_sql_constraints = [
		('name_key', 'UNIQUE (name)', 'You can not have two color with the same name !')
	]

	name = fields.Char(string="Name", required=True)
	description = fields.Text(string='Description')
	image_1920 = fields.Image("Fabric Image")
	fabric_color_line = fields.One2many('fabric.color.line', 'fabric_id', string="Fabric Color")
	image_1920 = fields.Image("Image")


class FabricColorLine(models.Model):
	_name = "fabric.color.line"
	_rec_name = "color_id"

	fabric_id = fields.Many2one('vvm.model.fabric', string="Fabric")
	color_id = fields.Many2one("model.color", string="Fabric Color")
	short_name = fields.Char(string="Short Name")
