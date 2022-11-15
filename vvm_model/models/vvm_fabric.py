# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VVMFabric(models.Model):
	_name = 'vvm.model.fabric'
	_description = 'VVM Fabric'
	_rec_name = 'name'

	name = fields.Char(string="Name", required=True)
	description = fields.Text(string='Description')
	image_1920 = fields.Image("Fabric Image")
	fabric_color_line = fields.One2many('fabric.color.line', 'fabric_id', string="Fabric Color")


class FabricColorLine(models.Model):
	_name = "fabric.color.line"
	_rec_name = "color_id"

	fabric_id = fields.Many2one('vvm.model.fabric', string="Fabric")
	color_id = fields.Many2one("model.color", string="Fabric Color")
