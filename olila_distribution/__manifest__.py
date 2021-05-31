# -*- coding: utf-8 -*-
{
    'name': "olila_distribution",

    'summary': 'This module incorporates olila distribution flow with delivery order ',

    'description': """
       olila Distribution
    """,

    'author': "mhasan@renga.tech",
    'website': "http://www.yourcompany.com",

    'category': 'stock',
    'version': '0.1',

    'depends': ['base','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/distribution_security.xml',
        'data/olila_data.xml',
        'views/vehicle_distribution_view.xml',
        'views/stock_picking_view.xml',
        
    ],
    # only loaded in demonstration mode
}
