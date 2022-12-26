from odoo import api, fields, models, _
from datetime import date
import requests


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", readonly=1, store=True)
    sale_partner_id = fields.Many2one('res.partner', string="Client Name", readonly=1, store=True)


    @api.onchange('currency_id')
    def currency_onchange(self):
        if self.currency_id.name == 'AED':
            for line in self.order_line:
                line.price_unit = line.product_id.standard_price
        if self.currency_id.name == 'EUR':
            for line in self.order_line:
                #line.price_unit = line.product_id.standard_price
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
                            line.price_unit = line.product_id.standard_price * original_rates
