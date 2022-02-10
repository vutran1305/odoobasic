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
     'version': '13.0.1',
     'depends': ['base'],
     'data': [  'views/library_book.xml',
                'security/groups.xml',
                'security/ir.model.access.csv',
              ],
     'demo': ['demo.xml'],
    'installable': True,
    'application': True,



 }
