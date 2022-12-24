# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID, _, api, fields, models
from re import findall as regex_findall
from re import split as regex_split


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    model_no_id = fields.Many2one("vvm.model", string="Model No.")
    model_type = fields.Char(string="Type")
    subtype = fields.Char(string="Sub-Type")
    fabric_id = fields.Many2one("vvm.model.fabric", string="Fabric")
    color_ids = fields.Many2many("fabric.color.line", string="Color")
    finish_category_id = fields.Many2one('finish.category', string="Finish Category")
    finish_color_ids = fields.Many2many("finish.category.color.line", string="Finish Color")
    location_id = fields.Many2one('stock.location', string="Location")
    reserved = fields.Boolean(string="Reserved")

    @api.model_create_multi
    def create(self, vals_list):
        res_ids = super(ProductionLot, self).create(vals_list)
        for res in res_ids:
            move_line = self.env['stock.move.line'].search([('product_id', '=', res.product_id.id),
                                                            ('lot_name', '=', res.name)])
            for move in move_line:
                res.model_no_id = move.move_id.purchase_model_no_id.id
                res.model_type = move.move_id.purchase_model_type
                res.subtype = move.move_id.purchase_subtype
                res.fabric_id = move.move_id.purchase_fabric_id.id
                res.finish_category_id = move.move_id.purchase_finish_category_id.id
                res.color_ids = [(6, 0, move.move_id.color_ids.ids)]
                res.finish_color_ids = [(6, 0, move.move_id.finish_color_ids.ids)]
                res.location_id = move.location_dest_id.id
        return res_ids


    @api.model
    def generate_lot_names(self, first_lot, count):
        """Generate `lot_names` from a string."""
        # We look if the first lot contains at least one digit.
        caught_initial_number = regex_findall(r"\d+", first_lot)
        if not caught_initial_number:
            return self.generate_lot_names(first_lot + "0", count)
        # We base the series on the last number found in the base lot.
        initial_number = caught_initial_number[-1]
        padding = len(initial_number)
        # We split the lot name to get the prefix and suffix.
        splitted = regex_split(initial_number, first_lot)
        # initial_number could appear several times, e.g. BAV023B00001S00001
        prefix = initial_number.join(splitted[:-1])
        suffix = splitted[-1]
        initial_number = int(initial_number)
        lot_names = []
        for i in range(0, count):
            lot_names.append('%s%s%s' % (
                prefix,
                str(initial_number + i).zfill(padding),
                suffix
            ))
        return lot_names


class Picking(models.Model):
    _inherit = "stock.picking"

    warehouse_user_id = fields.Many2one("res.users", string="Warehouse User")

    def send_mail_to_warehouse(self):
        if self.warehouse_user_id:
            template = self.env.ref("vvm_model.email_template_send_to_warehouse_user",
                                    raise_if_not_found=False)
            template.sudo().send_mail(self.id, force_send=True,email_values={"email_to": self.warehouse_user_id.login})


# VG Code For First SN	in Recipt
class StockMove(models.Model):
    _inherit = 'stock.move'

    product_no_id = fields.Many2one("product.product", string="Model No.",
                                    related='sale_line_id.product_no_id', store=True)
    model_no_id = fields.Many2one("vvm.model", string="Model No.",
                                  related='sale_line_id.model_no_id', store=True)
    model_type = fields.Char(string="Type", related='sale_line_id.model_type', store=True)
    subtype = fields.Char(string="Sub-Type", related='sale_line_id.subtype', store=True)
    fabric_id = fields.Many2one("vvm.model.fabric", string="Fabric", store=True)
    color_ids = fields.Many2many("fabric.color.line", string="Color", store=True)
    finish_category_id = fields.Many2one('finish.category', string="Finish Category", store=True)
    finish_color_ids = fields.Many2many("finish.category.color.line", string="Finish Color", store=True)

    purchase_product_no_id = fields.Many2one("product.product", string="Model No.",
                                             related='purchase_line_id.product_no_id', store=True)
    purchase_model_no_id = fields.Many2one("vvm.model", string="Model No.",
                                           related='purchase_line_id.model_no_id', store=True)
    purchase_model_type = fields.Char(string="Type", related='purchase_line_id.model_type', store=True)
    purchase_subtype = fields.Char(string="Sub-Type", related='purchase_line_id.subtype', store=True)
    #purchase_color_ids = fields.Many2many("fabric.color.line", string="Color")
    purchase_finish_category_id = fields.Many2one(related='purchase_line_id.finish_category_id',
                                                  string="Finish Category", store=True)
    purchase_fabric_id = fields.Many2one(related='purchase_line_id.fabric_id', string="Fabric", store=True)
    #purchase_finish_color_ids = fields.Many2many("finish.category.color.line", string="Finish Color", store=True)

    @api.model
    def create(self, vals):
        res = super(StockMove, self).create(vals)
        if res.sale_line_id:
            res.color_ids = [(6, 0, res.sale_line_id.color_ids.ids)]
            res.finish_color_ids = [(6, 0, res.sale_line_id.finish_color_ids.ids)]
        if res.purchase_line_id:
            res.color_ids = [(6, 0, res.purchase_product_no_id.color_ids.ids)]
            res.finish_color_ids = [(6, 0, res.purchase_product_no_id.finish_color_ids.ids)]
        return res

    @api.onchange('product_id')
    def onchange_purchase_line_id(self):
        if self.purchase_line_id:
            self.color_ids = [(6, 0, self.purchase_product_no_id.color_ids.ids)]
            self.finish_color_ids = [(6, 0, self.purchase_product_no_id.finish_color_ids.ids)]
        if self.sale_line_id:
            self.color_ids = [(6, 0, self.sale_line_id.color_ids.ids)]
            self.finish_color_ids = [(6, 0, self.sale_line_id.finish_color_ids.ids)]

    @api.onchange('product_no_id')
    def onchange_product_no_id_method(self):
        if self.product_no_id:
            self.model_type = self.product_no_id.model_type
            self.subtype = self.product_no_id.subtype
            self.fabric_id = self.product_no_id.fabric_id.id
            self.finish_category_id = self.product_no_id.finish_category_id.id
            self.color_ids = [(6, 0, self.purchase_product_no_id.color_ids.ids)]
            self.finish_color_ids = [(6, 0, self.purchase_product_no_id.finish_color_ids.ids)]

    @api.onchange('model_no_id')
    def onchange_model_no_id_method(self):
        if self.model_no_id:
            products = self.env["product.product"].sudo().search([('model_no_id', '=', self.model_no_id.id)])
            return {'domain': {'product_id': [('id', 'in', products.ids)]}}

    @api.onchange('purchase_model_no_id')
    def onchange_purchase_model_no_id_method(self):
        if self.purchase_model_no_id:
            products = self.env["product.product"].sudo().search([('model_no_id', '=', self.model_no_id.id)])
            return {'domain': {'product_id': [('id', 'in', products.ids)]}}

    def action_show_details(self):
        self.ensure_one()
        action = super().action_show_details()
        if self.origin:
            purchase_order = self.env["purchase.order"].sudo().search([('name','=',self.origin)])
            if purchase_order and self.product_id:
                next_serial = self.origin + '-' + self.product_id.name
                if self.product_id.fabric_id and self.product_id.fabric_id.name and len(self.product_id.fabric_id.name)>=4:
                    next_serial = next_serial + '-' + self.product_id.fabric_id.name[-4:]
                if self.product_id.color_ids and self.product_id.color_ids[0].color_id and len(self.product_id.color_ids[0].color_id.name)>=4:
                    next_serial = next_serial + '-' + self.product_id.color_ids[0].color_id.name[-4:]
                next_serial = next_serial + '-' + '0001'
                self.next_serial = next_serial
        return action


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    state = fields.Selection([('available', 'Item to sale'),
                              ('reserved', 'Reserved'),
                              ('not_available', 'Sold')],
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
            else:
                quant.state = 'not_available'
