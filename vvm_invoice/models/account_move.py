# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
	_inherit = 'account.move'

	sale_order_id = fields.Many2one('sale.order', string="Sale Order")
	sale_total_amount = fields.Float(string="Sale Order Total Amount")

