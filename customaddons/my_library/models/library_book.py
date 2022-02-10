from odoo import models, fields, api
from datetime import timedelta


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'  # Mo ta
    _inherit = 'base.archive'
    _order = 'date_release desc, name'  # Sap xep record , desc : giam dan
    _rec_name = 'short_name'  # Ten dai dien , vd (default) book/1 => book/short_name
    _sql_constraints = [  # Rang buoc csdl
        ('name_uniq', 'UNIQUE (name)',
         'Book title must be unique.'),
        ('positive_page', 'CHECK(pages>0)',
         'No of pages must be positive')
    ]

    name = fields.Char('Title', required=True)
    short_name = fields.Char('Short Title', translate=True, index=True)
    notes = fields.Text('Internal Notes')
    state = fields.Selection(
        [('draft', 'Not Available'),
         ('available', 'Available'),
         ('lost', 'Lost')],
        'State', default="draft")
    description = fields.Html('Description', sanitize=True, strip_style=False)
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_release = fields.Date('Release Date')
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of Pages',
                           groups='base.group_user',
                           states={'lost': [('readonly', True)]},
                           help='Total book page count', company_dependent=False)
    reader_rating = fields.Float('Reader Average Rating', digits=(14, 4),  # Optional precision decimals,
                                 )
    author_ids = fields.Many2many('res.partner', string='Authors')
    cost_price = fields.Float('Book Cost', digits='Book price')
    currency_id = fields.Many2one('res.currency', string='Currency')
    retail_price = fields.Monetary('Retail Price',
                                   # optional: currency_field='currency_id',
                                   )
    category_id = fields.Many2one('library.book.category')
    publisher_id = fields.Many2one('res.partner', string='Publisher',
                                   # optional:
                                   ondelete='set null',
                                   context={},
                                   domain=[],
                                   )

    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',  # nghich dao , su dung khi field da dc tinh toan nhung van muon sua thu cong
        search='_search_age',
        store=False,  # optional
        compute_sudo=True  # optional
    )

    publisher_city = fields.Char(
        'Publisher City',
        related='publisher_id.city',
        readonly=True)

    ref_doc_id = fields.Reference(
        selection='_referencable_models',
        string='Reference Document')

    # func tuy chinh rec_nam cua record
    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
        result.append((record.id, rec_name))
        return result

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past')

    # cal age_days
    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        # convert the operator:
        # book with age > value have a date < value_date
        operator_map = {
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([
            ('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]



