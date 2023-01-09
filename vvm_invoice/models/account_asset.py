# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date


class AccountAsset(models.Model):
	_inherit = 'account.asset'

	asset_number = fields.Char(string="Asset Number", readonly=True, states={'draft': [('readonly', False)]},
							   index=True, default=lambda self: _('New'))

	@api.model
	def create(self, vals):
		country_code = self.env.company.country_id.code
		year = date.today().year
		seq = self.env['ir.sequence'].next_by_code('account.asset')
		vals['asset_number'] = str(country_code)+'/'+str(year)+'/'+str(seq) #self.env['ir.sequence'].next_by_code('account.asset')
		res = super(AccountAsset, self).create(vals)
		return res