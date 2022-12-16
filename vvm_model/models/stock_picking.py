# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID, _, api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    warehouse_user_id = fields.Many2one("res.users", string="Warehouse User")

    def send_mail_to_warehouse(self):
        print ("-----------Mail sent to warehouse--------")
        if self.warehouse_user_id:
            print("-----------Mail sent to warehouse--------",self.warehouse_user_id)
            template = self.env.ref("vvm_model.email_template_send_to_warehouse_user",
                                    raise_if_not_found=False)
            print("-----------Mail sent to warehouse-----template---", template)
            template.sudo().send_mail(self.id, force_send=True,email_values={"email_to": self.warehouse_user_id.login})


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
            else:
                quant.state = 'not_available'
<<<<<<< HEAD



class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def generate_lot_names(self, first_lot, count):
        """Generate `lot_names` from a string."""
        # We look if the first lot contains at least one digit.
        print("------******-------", first_lot, count)
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
        print("=======prefix========", prefix)
        print("-----initial_number----", initial_number)
        print("-----suffix----", suffix)
        lot_names = []
        for i in range(0, count):
            lot_names.append('%s%s%s' % (
                prefix,
                str(initial_number + i).zfill(padding),
                suffix
            ))
            print("===============", lot_names)

        return lot_names
=======
>>>>>>> c38f194e203266d67d65bdf77dc051cd0d7aca74
