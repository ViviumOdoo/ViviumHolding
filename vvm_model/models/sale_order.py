# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    po_created = fields.Boolean(string="PO Created")

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
            'sale_order_id': self.id
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


    def copy_data(self, default=None):
        print ("***********",self)
        copy_record = super(SaleOrder, self).copy_data(default)
        print("*****copy_record******", copy_record)
        self.origin = self.name
        return copy_record
