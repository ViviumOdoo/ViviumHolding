# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID, _, api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    def send_mail_to_warehouse(self):
        print ("-----------Mail sent to warehouse--------")