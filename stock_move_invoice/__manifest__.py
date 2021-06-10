# -*- coding: utf-8 -*-

{
    'name': "Invoice From Stock Picking",
    'version': '14.0.1.0.0',
    'summary': """In this module creating customer invoice,vendor bill, customer credit note and refund from stock picking""",
    'description': """In this module creating customer invoice,vendor bill, customer
    credit note and refund from stock picking""",
    'category': 'Stock',
    'depends': ['stock', 'account'],
    'data': [
        #'security/ir.model.access.csv',
        'views/account_move_inherited.xml',
        'views/stock_picking_inherited.xml',
        'views/res_config_settings_inherited.xml',
    ],
    'installable': True,
    'application': True,
}
