# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
import requests


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    custom_name = fields.Char(string="Name")
    model_no_id = fields.Many2one("vvm.model", string="Model No.", required=True)
    name = fields.Char('Name', index=True, translate=True, readonly=True, store=True, required=False)
    default_code = fields.Char('Vendor Reference', compute='_compute_default_code',
                               inverse='_set_default_code', store=True)
    model_name = fields.Char(string="Model Name")
    model_type = fields.Char(string="Type", required=True, size=4)
    subtype = fields.Char(string="Sub-Type", size=2)
    item_code_id = fields.Many2one("product.product", string="Item Code")
    fabric_id = fields.Many2one("vvm.model.fabric", string="Fabric")
    color_ids = fields.Many2many("fabric.color.line", string="Color")
    finish_category_id = fields.Many2one('finish.category', string="Finish Category")
    finish_color_ids = fields.Many2many("finish.category.color.line", string="Finish Color")
    sale_price_aed = fields.Float(string="Sale Price (EUR)")
    purchase_price_aed = fields.Float(string="Purchase Price (EUR)")
    image_dimension = fields.Image("Dimension Image")


    @api.onchange('finish_category_id')
    def onchange_finish_category(self):
        if self.finish_category_id:
            self.finish_color_ids = [(6, 0, [])]

    @api.onchange('fabric_id')
    def onchange_fabric_id(self):
        if self.fabric_id:
            self.color_ids = [(6, 0, [])]

    @api.onchange('sale_price_aed')
    def onchange_sale_price_aed(self):
        if self.sale_price_aed:
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
                        self.list_price = self.sale_price_aed / original_rates

    @api.onchange('purchase_price_aed')
    def onchange_purchase_price_aed(self):
        if self.purchase_price_aed:
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
                        self.standard_price = self.purchase_price_aed / original_rates

    @api.onchange('model_no_id')
    def onchange_model_no_id_method(self):
        if self.model_no_id:
            self.model_name = self.model_no_id.model_name

    @api.model
    def create(self, values):
        if values.get('model_no_id'):
            vvm_model = self.env['vvm.model'].sudo().browse([values.get('model_no_id')])
            if vvm_model:
                values['name'] = vvm_model.model_no + values['model_type'] + values['subtype']
                values['custom_name'] = vvm_model.model_no + '/' + values['model_type'] + '/' + values['subtype']
                values['barcode'] = vvm_model.model_no + values['model_type'] + values['subtype']
        res = super(ProductTemplate, self).create(values)
        return res

    def action_storable_product_template(self):
        product_consu_ids = self.env['product.template'].search([('detailed_type', '=', 'consu')])
        for consu in product_consu_ids:
            consu.detailed_type = 'product'


class ProductProduct(models.Model):
    _inherit = 'product.product'

    _sql_constraints = [('barcode_uniq', 'Check(1=1)', 'Barcode must be unique per Company!'), ]

    default_code = fields.Char('Vendor Reference', index=True)

    # @api.constrains('barcode', 'company_id')
    # def _check_barcode_company_id(self):
    #     for i in self.env['product.product'].search([]):
    #         if i.id:
    #             if self.barcode == i.barcode and self.company_id == i.company_id:
    #                 raise ValidationError(_("Barcode 1 must be unique per Company!"))


    def name_get(self):
        result = []
        if self.env.context.get('default_is_model'):
            for product in self:
                if product.custom_name:
                    name = product.custom_name
                else:
                    name = product.name
                result.append((product.id, name))
            return result
        return super(ProductProduct, self).name_get()

    @api.onchange('sale_price_aed')
    def onchange_sale_price_aed(self):
        if self.sale_price_aed:
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
                        self.list_price = self.sale_price_aed / original_rates

    @api.onchange('purchase_price_aed')
    def onchange_purchase_price_aed(self):
        if self.purchase_price_aed:
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
                        self.standard_price = self.purchase_price_aed / original_rates

    @api.onchange('model_no_id')
    def onchange_model_no_id_method(self):
        if self.model_no_id:
            self.model_name = self.model_no_id.model_name

    @api.model
    def create(self, values):
        if values.get('model_no_id'):
            vvm_model = self.env['vvm.model'].sudo().browse([values.get('model_no_id')])
            if vvm_model:
                values['name'] = vvm_model.model_no + values['model_type'] + values['subtype']
                values['custom_name'] = vvm_model.model_no + '/' + values['model_type'] + '/' + values['subtype']
                values['barcode'] = vvm_model.model_no + values['model_type'] + values['subtype']
        res = super(ProductProduct, self).create(values)
        return res

    def action_storable_product(self):
        product_consu_ids = self.env['product.product'].search([('detailed_type', '=', 'consu')])
        for consu in product_consu_ids:
            consu.detailed_type = 'product'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_no_id = fields.Many2one("product.product", string="Model No.")
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price',
                              default=0.0, readonly=True, store=True)
    model_no_id = fields.Many2one("vvm.model", string="Model No.")
    model_type = fields.Char(string="Type")
    subtype = fields.Char(string="Sub-Type")
    fabric_id = fields.Many2one("vvm.model.fabric", string="Fabric")
    color_ids = fields.Many2many("fabric.color.line", string="Color")
    finish_category_id = fields.Many2one('finish.category', string="Finish Category")
    finish_color_ids = fields.Many2many("finish.category.color.line", string="Finish Color")
    stock_production_lot_id = fields.Many2one("stock.production.lot", string="Serial number")

    def _prepare_invoice_line(self, **optional_values):
        values = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if self.product_no_id:
            values['product_no_id'] = self.product_no_id.id
        if self.model_type:
            values['model_type'] = self.model_type
        if self.subtype:
            values['subtype'] = self.subtype
        if self.fabric_id:
            values['fabric_id'] = self.fabric_id.id
        if self.finish_category_id:
            values['finish_category_id'] = self.finish_category_id.id
        return values

    # @api.onchange('product_id')
    # def onchange_product_model(self):
    #     if self.product_id:
    #         self.model_no_id = self.product_id.model_no_id.id
    #         self.model_type = self.product_id.model_type
    #         self.subtype = self.product_id.subtype
    #         self.fabric_id = self.product_id.fabric_id.id
    #         self.finish_category_id = self.product_id.finish_category_id.id

    @api.onchange('stock_production_lot_id')
    def onchange_stock_production_lot(self):
        if self.stock_production_lot_id:
            self.product_id = self.stock_production_lot_id.product_id.id
            self.model_no_id = self.stock_production_lot_id.model_no_id.id
            self.model_type = self.stock_production_lot_id.model_type
            self.subtype = self.stock_production_lot_id.subtype
            self.fabric_id = self.stock_production_lot_id.fabric_id.id
            self.finish_category_id = self.stock_production_lot_id.finish_category_id.id
            self.finish_color_ids = [(6, 0, self.stock_production_lot_id.finish_color_ids.ids)]
            self.color_ids = [(6, 0, self.stock_production_lot_id.color_ids.ids)]

    # @api.onchange('product_no_id')
    # def onchange_product_no_id_method(self):
    #     if self.product_no_id:
    #         self.model_type = self.product_no_id.model_type
    #         self.subtype = self.product_no_id.subtype
    #         self.fabric_id = self.product_no_id.fabric_ids.ids
    #         self.color_ids = self.product_no_id.color_ids.ids
    #         if self.product_no_id.custom_name:
    #             products = self.env["product.product"].sudo().search([('custom_name', '=', self.product_no_id.custom_name)])
    #             if len(products) == 1:
    #                 self.product_id = products.id
    #             elif len(products) > 1:
    #                 return {'domain': {'product_id': [('id', 'in', products.ids)]}}

    # @api.onchange('model_no_id')
    # def onchange_model_no_id_method(self):
    #     if self.model_no_id:
    #         products = self.env["product.product"].sudo().search([('model_no_id','=',self.model_no_id.id)])
    #         return {'domain': {'product_id': [('id', 'in', products.ids)]}}


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_no_id = fields.Many2one("product.product", string="Model No.")
    model_no_id = fields.Many2one("vvm.model", string="Model No.")
    model_type = fields.Char(string="Type")
    subtype = fields.Char(string="Sub-Type")
    fabric_id = fields.Many2one("vvm.model.fabric", string="Fabric")
    color_ids = fields.Many2many("fabric.color.line", string="Color")
    finish_category_id = fields.Many2one('finish.category', string="Finish Category")
    finish_color_ids = fields.Many2many("finish.category.color.line", string="Finish Color")

    def _prepare_account_move_line(self, move=False):
        values = super(PurchaseOrderLine, self)._prepare_account_move_line(move=False)
        if self.product_no_id:
            values['product_no_id'] = self.product_no_id.id
        if self.model_type:
            values['model_type'] = self.model_type
        if self.subtype:
            values['subtype'] = self.subtype
        if self.fabric_id:
            values['fabric_id'] = self.fabric_id.id
        if self.finish_category_id:
            values['finish_category_id'] = self.finish_category_id.id
        return values

    # @api.onchange('product_no_id')
    # def onchange_product_no_id_method(self):
    #     if self.product_no_id:
    #         self.model_type = self.product_no_id.model_type
    #         self.subtype = self.product_no_id.subtype
    #         self.fabric_id = self.product_no_id.fabric_ids.ids
    #         self.color_ids = self.product_no_id.color_ids.ids
    #         if self.product_no_id.custom_name:
    #             products = self.env["product.product"].sudo().search(
    #                 [('custom_name', '=', self.product_no_id.custom_name)])
    #             if len(products) == 1:
    #                 self.product_id = products.id
    #             elif len(products) > 1:
    #                 return {'domain': {'product_id': [('id', 'in', products.ids)]}}

    # @api.onchange('model_no_id')
    # def onchange_model_no_id_method(self):
    #     if self.model_no_id:
    #         products = self.env["product.product"].sudo().search([('model_no_id', '=', self.model_no_id.id)])
    #         return {'domain': {'product_id': [('id', 'in', products.ids)]}}

    @api.onchange('product_id')
    def onchange_product_id_method(self):
        if self.product_id:
            self.model_no_id = self.product_id.model_no_id.id
            self.model_type = self.product_id.model_type
            self.subtype = self.product_id.subtype
            self.fabric_id = self.product_id.fabric_id.id
            self.finish_category_id = self.product_id.finish_category_id.id


# class StockMove(models.Model):
#     _inherit = 'stock.move'
#
#     product_no_id = fields.Many2one("product.product", string="Model No.",
#                                     related='sale_line_id.product_no_id', store=True)
#     model_no_id = fields.Many2one("vvm.model", string="Model No.",
#                                   related='sale_line_id.model_no_id', store=True)
#     model_type = fields.Char(string="Type", related='sale_line_id.model_type', store=True)
#     subtype = fields.Char(string="Sub-Type", related='sale_line_id.subtype', store=True)
#     fabric_id = fields.Many2one("vvm.model.fabric", string="Fabric", store=True)
#     color_ids = fields.Many2many("fabric.color.line", string="Color", store=True)
#     finish_category_id = fields.Many2one('finish.category', string="Finish Category", store=True)
#     finish_color_ids = fields.Many2many("finish.category.color.line", string="Finish Color", store=True)
#
#     purchase_product_no_id = fields.Many2one("product.product", string="Model No.",
#                                              related='purchase_line_id.product_no_id', store=True)
#     purchase_model_no_id = fields.Many2one("vvm.model", string="Model No.",
#                                            related='purchase_line_id.model_no_id', store=True)
#     purchase_model_type = fields.Char(string="Type", related='purchase_line_id.model_type', store=True)
#     purchase_subtype = fields.Char(string="Sub-Type", related='purchase_line_id.subtype', store=True)
#     purchase_color_ids = fields.Many2many("fabric.color.line", string="Color")
#     purchase_finish_category_id = fields.Many2one(related='purchase_line_id.finish_category_id',
#                                                   string="Finish Category", store=True)
#     purchase_fabric_id = fields.Many2one(related='purchase_line_id.fabric_id', string="Fabric", store=True)
#     purchase_finish_color_ids = fields.Many2many("finish.category.color.line", string="Finish Color", store=True)
#
#     @api.model
#     def create(self, vals):
#         res = super(StockMove, self).create(vals)
#         if res.sale_line_id:
#             res.color_ids = res.sale_line_id.color_ids.ids
#             res.finish_color_ids = res.sale_line_id.finish_color_ids.ids
#         if res.purchase_line_id:
#             res.purchase_color_ids = res.purchase_product_no_id.color_ids.ids
#             res.purchase_finish_color_ids = res.purchase_product_no_id.finish_color_ids.ids
#         return res
#
#     @api.onchange('purchase_line_id')
#     def onchange_purchase_line_id(self):
#         if self.purchase_product_no_id:
#             self.purchase_color_ids = self.purchase_product_no_id.color_ids.ids
#             self.purchase_finish_color_ids = self.purchase_product_no_id.finish_color_ids.ids
#
#     @api.onchange('sale_line_id')
#     def onchange_sale_line_id(self):
#         if self.sale_line_id:
#             self.color_ids = self.sale_line_id.color_ids.ids
#             self.finish_color_ids = self.sale_line_id.finish_color_ids.ids
#
#     @api.onchange('product_no_id')
#     def onchange_product_no_id_method(self):
#         if self.product_no_id:
#             self.model_type = self.product_no_id.model_type
#             self.subtype = self.product_no_id.subtype
#             self.fabric_id = self.product_no_id.fabric_id.id
#             self.finish_category_id = self.product_no_id.finish_category_id.id
#
#     @api.onchange('model_no_id')
#     def onchange_model_no_id_method(self):
#         if self.model_no_id:
#             products = self.env["product.product"].sudo().search([('model_no_id', '=', self.model_no_id.id)])
#             return {'domain': {'product_id': [('id', 'in', products.ids)]}}
#
#     @api.onchange('purchase_model_no_id')
#     def onchange_purchase_model_no_id_method(self):
#         if self.purchase_model_no_id:
#             products = self.env["product.product"].sudo().search([('model_no_id', '=', self.model_no_id.id)])
#             return {'domain': {'product_id': [('id', 'in', products.ids)]}}


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_no_id = fields.Many2one("product.product", string="Model No.")
    model_type = fields.Char(string="Type")
    subtype = fields.Char(string="Sub-Type")
    fabric_id = fields.Many2one("vvm.model.fabric", string="Fabric")
    color_ids = fields.Many2many("fabric.color.line", string="Color")
    finish_category_id = fields.Many2one('finish.category', string="Finish Category")
    finish_color_ids = fields.Many2many("finish.category.color.line", string="Finish Color")

    @api.onchange('product_no_id')
    def onchange_product_no_id_method(self):
        if self.product_no_id:
            self.model_type = self.product_no_id.model_type
            self.subtype = self.product_no_id.subtype
            self.fabric_id = self.product_no_id.fabric_id.id
            self.finish_category_id = self.product_no_id.finish_category_id.id
