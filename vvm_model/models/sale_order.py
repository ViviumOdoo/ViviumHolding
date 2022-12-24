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
    discount_payment = fields.Float(string='Advance Percentage')
    discount_amount = fields.Float(compute='_amount_due', string="Advance Amount", store=True)
    fixed_payment = fields.Float(string="Advance Amount", store=True)
    amount_due = fields.Float(string="Amount Due", compute='_amount_due', store=True)

    # VG Code
    project_reference = fields.Char(string="Project Reference")
    sales_type = fields.Selection([('retails', 'Retails'), ('project', 'Project')],
                                    default='retails', string='Sales Type')

    @api.depends('fixed_payment', 'discount_payment', 'down_payment')
    def _amount_due(self):
        """
        Compute the due amounts of the SO.
        """
        for order in self:
            amount_due = discount_amount = 0.0
            if order.down_payment == 'discount':
                order.fixed_payment = 0.0
                amount_due += order.amount_total * (1 - (order.discount_payment or 0.0) / 100.0)
                discount_amount = order.amount_total - amount_due
            else:
                order.discount_payment = 0.0
                order.discount_amount = 0.0
                amount_due += order.amount_total - order.fixed_payment
            order.update({
                'amount_due': amount_due,
                'discount_amount': discount_amount,
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
                'price_unit': line.product_id.lst_price or 1,
            })

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order_line in self.order_line:
            if order_line.stock_production_lot_id:
                order_line.stock_production_lot_id.reserved = True
        return res
