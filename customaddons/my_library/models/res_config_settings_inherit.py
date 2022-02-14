from odoo import models, fields, api
class ResConfigSettings(models.TransientModel):
     _inherit = 'res.config.settings'
     group_self_borrow = fields.Boolean(string="Selfborrow",implied_group='my_library.group_self_borrow')