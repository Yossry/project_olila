# -*- coding: utf-8 -*-
{
    'name' : 'Sale Delivery by Date',
    'category': 'Sale',
    'version': '14.0.1.0',
    'description': """
        This Module allows to create delivery order based on delivery date in sale order line.
        * Allows you to create delivery order based on delivey date from sale order lines.
        * Allows you to change delivery date for multiple product at a single time.
    """,
    'depends' : ['base', 'sale_management', 'sale_stock'],
    'data': [
        'views/sale_order_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

