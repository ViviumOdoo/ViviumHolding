# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class FinishCategory(models.Model):
	_name = 'finish.category'
	_description = 'Finish Category'
	_sql_constraints = [
		('name', 'UNIQUE (name)', 'You can not have two Finish Category with the same name !')
	]

	name = fields.Char(string="Name", required=True)
	finish_color_line = fields.One2many('finish.category.color.line', 'finish_id', string="Finish Color")
	is_created = fields.Boolean(string="Is Created")
	image_128 = fields.Image("Image")

	@api.model
	def create(self, vals):
		vals['is_created'] = True
		result = super(FinishCategory, self).create(vals)
		return result


class FinishCategoryColorLin(models.Model):
	_name = "finish.category.color.line"
	_rec_name = "color_id"

	finish_id = fields.Many2one('finish.category', string="Finish Category")
	color_id = fields.Many2one("model.color", string="Finish Color")
	short_name = fields.Char(string="Short Name")
