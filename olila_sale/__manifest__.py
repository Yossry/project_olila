# -*- coding: utf-8 -*-
{
    'name': "Olila Sales",
    'summary': """Olila Sales""",
    'description': """ Olila Sales """,
    'author': "Preciseways",
    'website': "http://www.preciseways.com",
    'version': '14.0',
    'depends': ['sale_management', 'stock', 'fleet'],
    'data': [
        'security/ir.model.access.csv',
        'data/blial_seq.xml',
        'views/res_partner_view.xml',
        'views/sale_view.xml',
        'views/cost_estimation.xml',
        'views/stock_picking.xml',
    ],
}