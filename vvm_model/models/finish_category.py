# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class FinishCategory(models.Model):
	_name = 'finish.category'
	_description = 'Finish Category'
	_rec_name = 'name'

	name = fields.Char(string="Name", required=True)
	finish_color_line = fields.One2many('finish.category.color.line', 'finish_id', string="Fabric Color")
	is_created = fields.Boolean(string="Is Created")

	def write(self, vals):
		if self.id > 0:
			raise UserError(_("No edit in once record is saved"))
		else:
			return super().write(vals)

	@api.model
	def create(self, vals):
		vals['is_created'] = True
		result = super(FinishCategory, self).create(vals)
		return result


class FinishCategoryColorLin(models.Model):
	_name = "finish.category.color.line"
	_rec_name = "color_id"

	finish_id = fields.Many2one('finish.category', string="Fabric")
	color_id = fields.Many2one("model.color", string="Fabric Color")
