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
     'category': 'Library',
      'version': '13.0.1.0.1',
     'depends': ['board','base_setup'],

     'data': [  'data/data.xml',
                'security/ir.model.access.csv',
                'security/groups.xml',
                'security/library_security.xml',
                'views/library_book.xml',
                'views/library_book_categ.xml',
                'views/library_book_rent.xml',
                'views/settings_inherit_view.xml',
                # 'views/res_config_settings.xml',
                'views/dashboard_view.xml',
                'wizard/library_book_rent_wizard.xml',
                'wizard/library_book_return_wizard.xml',

              ],
    'demo': [
        'data/demo.xml',
    ],
    'installable': True,
    'application': True,



 }
