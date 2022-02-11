from odoo import models, fields
class LibraryBookCategory(models.Model):
    _inherit = 'library.book.category'

    max_borrow_days = fields.Integer(
        'Maximum borrow days',
        help="For how many days book can be borrowed",
        default=10)