# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    po_created = fields.Boolean(string="PO Created")
    payment_method_id = fields.Many2one('account.payment.method', string="Payment Method")
    payment_ref = fields.Char(string='Payment Reference No.')
    down_payment = fields.Selection([('discount','Percentage'),('fixed', 'Fixed Amount')],
                                    default='discount', string='Down Payment')
    discount_payment = fields.Float(string='Advance Paid')
    fixed_payment = fields.Float(string="Advance Paid")
    amount_due = fields.Float(string="Amount Due", compute='_amount_due', store=True)

    @api.depends('fixed_payment', 'discount_payment', 'down_payment')
    def _amount_due(self):
        """
        Compute the due amounts of the SO.
        """
        for order in self:
            amount_due = 0.0
            if order.down_payment == 'discount':
                order.fixed_payment = 0.0
                amount_due +=  order.amount_total * (1 - (order.discount_payment or 0.0) / 100.0)
            else:
                order.discount_payment = 0.0
                amount_due += order.amount_total - order.fixed_payment
            order.update({
                'amount_due': amount_due,
            })

    def _prepare_invoice(self):
        values = super(SaleOrder, self)._prepare_invoice()
        values['sale_order_id'] = self.id
        values['sale_total_amount'] = self.amount_total
        return values

    def action_create_po(self):
        po_id = self.env['purchase.order'].create({
            'date_planned': self.date_order,
            'user_id': self.user_id.id,
            'company_id': self.company_id.id,
            'origin': self.origin,
            'partner_id': self.env['res.partner'].search([('supplier_rank', '>=', 0)], limit=1).id,
            'sale_order_id': self.id,
            'sale_partner_id': self.partner_id.id
        })
        self.po_created = True
        for line in self.order_line:
            po_line_id = self.env['purchase.order.line'].create({
                'order_id': po_id.id,
                'product_id': line.product_id.id,
                'model_no_id': line.model_no_id.id,
                'model_type': line.model_type,
                'subtype': line.subtype,
                'fabric_id': line.fabric_id.id,
                'color_ids': line.color_ids.ids,
                'finish_category_id': line.finish_category_id.id,
                'finish_color_ids': line.finish_color_ids.ids,
                'name': line.name,
                'product_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
            })
