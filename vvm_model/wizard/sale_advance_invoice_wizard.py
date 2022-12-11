# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def _default_sale_order_id(self):
        if self._context.get('active_model') == 'sale.order' and self._context.get('active_id', False):
            sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
            return sale_order

    sale_id = fields.Many2one('sale.order', string="Sale Order", default=_default_sale_order_id)

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        if self.advance_payment_method == 'percentage':
            amount = self.default_get(['amount']).get('amount')
            return {'value': {'amount': amount}}
        return {}

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        if self.sale_id.down_payment:
            if self.advance_payment_method == 'fixed':
                amount = self.sale_id.fixed_payment
                return {'value': {'amount': amount}}
            elif self.advance_payment_method == 'percentage':
                amount = self.sale_id.discount_payment
                return {'value': {'amount': amount}}
            else:
                return {'value': {'amount': 0.0}}

