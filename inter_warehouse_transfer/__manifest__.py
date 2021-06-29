# -*- coding: utf-8 -*-

{
    'name': "Inter Warehouse Transfer",
    'version': '14.0',
    'summary': """Inter Warehouse Transfer""",
    'category': 'Stock',
    'depends': ['stock'],
    'data': [
        'data/stock_data.xml',
        'security/ir.model.access.csv',
        'views/stock_transfer_view.xml',
    ],
    'installable': True,
    'application': True,
}
