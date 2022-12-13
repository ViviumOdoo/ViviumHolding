# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID, _, api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    def send_mail_to_warehouse(self):
        print ("-----------Mail sent to warehouse--------")


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    state = fields.Selection([('available', 'Available'),
                              ('reserved', 'Reserved'),
                              ('not_available', 'Not Available')],
                             string="State", compute="_compute_state_quant")

    @api.depends('reserved_quantity', 'available_quantity')
    def _compute_state_quant(self):
        for quant in self:
            if quant.reserved_quantity <= 0 and quant.available_quantity <= 0:
                quant.state = 'not_available'
            elif quant.reserved_quantity <= 0 and quant.available_quantity > 0:
                quant.state = 'available'
            elif quant.reserved_quantity > 0 and quant.available_quantity > 0:
                quant.state = 'reserved'
