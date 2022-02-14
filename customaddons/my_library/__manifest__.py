{
    'name': 'My Library',
    'summary': "Manage books easily",
     'description': """
     Manage Library
     ==============
     Description related to library.
     """,
     'author': "Vu tran",
     'website': "http://www.example.com",
     'category': 'Uncategorized',
      'version': '13.0.1.0.1',
     'depends': ['base'],

     'data': [  'security/ir.model.access.csv',
                'data/data.xml',
                # 'data/demo.xml',
                'views/library_book.xml',
                'security/groups.xml',
                'views/library_book_categ.xml',
                'views/library_book_rent.xml',
                'views/settings_inherit_view.xml',
                'wizard/library_book_rent_wizard.xml',
                'wizard/library_book_return_wizard.xml',
              ],
    'demo': [
        'data/demo.xml',
    ],
    'installable': True,
    'application': True,



 }
