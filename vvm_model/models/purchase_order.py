from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    sale_partner_id = fields.Many2one('res.partner', string="Client Name")


    @api.onchange('currency_id')
    def currency_onchange(self):
        if self.currency_id.name == 'EUR':
            for line in self.order_line:
                line.price_unit = line.product_id.purchase_price_aed
        if self.currency_id.name == 'AED':
            for line in self.order_line:
                line.price_unit = line.product_id.standard_price
