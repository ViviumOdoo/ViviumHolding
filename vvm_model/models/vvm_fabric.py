# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VVMFabric(models.Model):
	_name = 'vvm.model.fabric'
	_description = 'VVM Fabric'
	_rec_name = 'name'

	name = fields.Char(string="Name", required=True)
	color_ids = fields.Many2many("model.color", string="Fabric Color")

