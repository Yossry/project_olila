# -*- coding: utf-8 -*-
{
    'name': "Sale Order Approval",

    'summary': """
        Sale Order Approval
        """,

    'description': """
    Sale Order Approval
    =========================
        Sale Order Approval- Only users with particular group access will be able to approve the order.
    """,

    'author': "",
    'website': "",
    "live_test_url": "",

    # Categories can be used to filter modules in modules listing

    # for the full list
    'category': 'sale',
    'version': '0.5',


    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/sale_views.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    "images":  [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
