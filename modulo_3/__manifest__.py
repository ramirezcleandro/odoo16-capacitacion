{
    'name': "Library Management",
    'version': '16.0.1',
    'license': 'LGPL-3',
    'summary': '',
    'description': "Book management system",
    'author': "Jr",
    'website': '',
    'depends': ['base', 'sale_purchase'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/library_book_views.xml',
        'wizard/obtain_book_information.xml'
    ],
    'installable': True,
    'assets': {
        "web.assets_backend": [
            "modulo_3/static/src/js/xlsx_custom_button.js",
            "modulo_3/static/src/xml/xlsx_custom_button.xml",
        ],
    },
}
