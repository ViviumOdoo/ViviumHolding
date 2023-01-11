# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
import requests
from datetime import datetime
import json
from lxml import etree


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
    project_reference = fields.Char(string="Project Reference")
    sales_type = fields.Selection([('retails', 'Retails'), ('project', 'Project')],
                                    default='retails', string='Sales Type')
    company_code = fields.Char(string="Company Code", default=lambda self: self.env.company.company_code)

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(SaleOrder, self).fields_view_get(view_id=view_id,
    #                                                      view_type=view_type,
    #                                                      toolbar=toolbar,
    #                                                      submenu=submenu)
    #     if self.env.company.company_code != 'VLC':
    #         doc = etree.XML(res['arch'])
    #         #print ("---------",doc.xpath("//field[@name='order_line']/field"))
    #         #print ("==========",doc.xpath("//form/sheet/notebook/page[@name='order_lines']/field[@name='order_line']/tree//field"))
    #         fields_name = 'model_no_id', 'product_no_id', 'model_type', 'subtype', 'fabric_id', 'color_ids', 'finish_category_id', 'finish_color_ids', 'stock_production_lot_id'
    #         for field in fields_name:
    #             for node in doc.xpath("//field[@name='order_line']/field[@name='%s']" % field):
    #                 node.set("invisible", "1")
    #                 modifiers = json.loads(node.get("modifiers"))
    #                 modifiers['invisible'] = True
    #                 node.set("modifiers", json.dumps(modifiers))
    #         res['arch'] = etree.tostring(doc)
    #     return res

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
            'sale_partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id
        })
        self.po_created = True
        for line in self.order_line:
            po_line_id = self.env['purchase.order.line'].create({
                'display_type': line.display_type,
                'product_no_id': line.product_no_id.id,
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
                'date_planned': datetime.today(),
                'taxes_id': False,
            })

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order_line in self.order_line:
            if order_line.stock_production_lot_id:
                order_line.stock_production_lot_id.reserved = 'reserved'
                order_line.stock_production_lot_id.sale_order_id = self.id
        return res

    @api.onchange('currency_id')
    def currency_onchange(self):
        if self.currency_id.name == 'AED':
            for line in self.order_line:
                line.price_unit = line.product_id.lst_price
        if self.currency_id.name == 'EUR':
            for line in self.order_line:
                # line.price_unit = line.product_id.standard_price
                today = date.today()
                url = 'https://api.exchangerate.host/timeseries?base=AED&start_date=' + str(today) + '&end_date=' + str(
                    today) + '&symbols=EUR'
                response = requests.get(url)
                data = response.json()
                if data.get('rates'):
                    rates_data = data.get('rates')
                    # print("=======rates_data=======",rates_data)
                    if rates_data.get(str(date.today())):
                        today_rates = rates_data.get(str(date.today()))
                        # print("======today_rates===",today_rates)
                        if today_rates.get('EUR'):
                            original_rates = round(today_rates.get('EUR'), 4)
                            # print("======original_rates===", original_rates)
                            line.price_unit = line.product_id.lst_price * original_rates

    def action_cancel(self):
        res = super().action_cancel()
        for sale_order in self:
            for line in sale_order.order_line:
                if line.product_id and line.stock_production_lot_id:
                    serial_ids = self.env['stock.production.lot'].search([('product_id', '=', line.product_id.id),
                                                             ('id', '=', line.stock_production_lot_id.id)])
                    for serial_id in serial_ids:
                        serial_id.reserved = 'unreserved'
                        serial_id.sale_order_id = False
        return res