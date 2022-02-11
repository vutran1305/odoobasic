from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError
from odoo.tools.translate import _

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'  # Mo ta
    _inherit = 'base.archive'
    #_order = 'date_release desc, name'  # Sap xep record , desc : giam dan
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

    state = fields.Selection([
        ('draft', 'Unavailable'),
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost', 'Lost')],
        'State', default="draft")
    manager_remarks = fields.Text('Manager Remarks')
    isbn = fields.Char('ISBN')
    old_edition = fields.Many2one('library.book', string='OldEdition')



    # func tuy chinh rec_nam cua record
    def name_get(self):
        result = []
        for book in self:
            authors = book.author_ids.mapped('name')
            name = '%s (%s)' % (book.name, ', '.join(authors))
            result.append((book.id, name))
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

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
               ('available', 'borrowed'),
               ('borrowed', 'available'),
               ('available', 'lost'),
               ('borrowed', 'lost'),
               ('lost', 'available')]
        return (old_state, new_state) in allowed

    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state,new_state):
                book.state = new_state
            else:
                continue

    def make_available(self):
        self.change_state('available')

    def make_borrowed(self):
        self.change_state('borrowed')

    def make_lost(self):
        self.change_state('lost')

    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                msg = _('Moving from %s to %s is notallowed') % (book.state, new_state)
                raise UserError(msg)

    def log_all_library_members(self):
    # This is an empty recordset of model library.member
        library_member_model = self.env['library.member']

        all_members = library_member_model.search([])
        print("ALL MEMBERS:", all_members)
        return True

    def change_release_date(self):
        self.ensure_one()
        self.date_release = fields.Date.today()


    """Searching for records ???"""
    def find_book(self):
        for record in self:
            domain = ['|', '&', ('name', 'ilike', 'Book Name'), ('category_id.name', 'ilike', 'CategoryName'), '&',
                  ('name', 'ilike', 'Book Name 2'), ('category_id.name', 'ilike', 'Category Name2')]
            books = record.search(domain)
            return True


    """Filtering recordsets ????"""
    @api.model
    def books_with_multiple_authors(self, all_books): #???
        def predicate(book):
            if len(book.author_ids) > 1:
                return True
            return False
        return all_books.filter(predicate)


    """Traversing recordset relations ????"""
    @api.model
    def get_author_names(self, all_books):
        return all_books.mapped('author_ids.city')

    """Sorting recordsets ???"""
    @api.model
    def sort_books_by_date(self, books):
        return books.sorted(key='release_date',reverse = True)



    """Extending write() and create()"""
    @api.model
    def create(self, values):
        if not self.user_has_groups('my_library.group_librarian'):
            if 'manager_remarks' in values:
                raise UserError(
                    'You are not allowed to modify '
                    'manager_remarks'
                )

        return super(LibraryBook, self).create(values)

    def write(self, values):
        if not self.user_has_groups('my_library.group_librarian'):
            if 'manager_remarks' in values:
                raise UserError(
                    'You are not allowed to modify '
                    'manager_remarks'
                )
        return super(LibraryBook, self).write(values)


    """Customizing how records are searched"""
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = [] if args is None else args.copy()
        for record in self:
            if not (name == '' and operator == 'ilike'):
                args += ['|', '|', ('name', operator, name),
                         ('isbn', operator, name),
                         ('author_ids.name', operator, name)
                         ]
        return super(LibraryBook, self)._name_search(name=name, args=args, operator=operator, limit=limit,
                                                     name_get_uid=name_get_uid)
    """Fetching data in groups using read_group()"""
    #Tinh trung binh cost price cua nhung cuon sach trong the loai nay
    @api.model
    def _get_average_cost(self):
        grouped_result = self.read_group(
            [('cost_price', "!=", False)],  # Domain
            ['category_id', 'cost_price:avg'],  # Fields to access
            ['category_id']  # group_by
        )
        return grouped_result
    """Invoking functions from XML files"""
    @api.model
    def update_book_price(self):
        all_books = self.search([])
        for book in all_books:
            book.cost_price += 20
