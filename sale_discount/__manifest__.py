# -*- coding: utf-8 -*-

{
    'name': 'Sale Discount (PWAY)',
    'version': '1.0',
    'sequence': 120,
    'category': 'customisation',
    'summary': 'Apply global discount on sale order',
    'description':'''
        Apply discount on sale order globally or discount by order lines.
        Discount can be applied fixed price or percentage.''',
    'depends': ['sale_management'],
    'data': [
        'views/sale_discount_view.xml',
    ],
    'installable': True,
    'application': True,
}