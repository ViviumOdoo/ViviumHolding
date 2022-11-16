from odoo import api, fields, models, tools, SUPERUSER_ID, _


class Users(models.Model):
    _inherit = "res.users"

    user_max_discount = fields.Float('Discount')