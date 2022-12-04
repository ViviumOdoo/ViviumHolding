from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    sale_partner_id = fields.Many2one('res.partner', string="Client Name")
