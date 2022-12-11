from odoo import api, fields, models, tools, SUPERUSER_ID, _


class Users(models.Model):
    _inherit = "res.users"

    user_max_discount = fields.Float('Discount')


class Partner(models.Model):
    _inherit = "res.partner"

    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.company)