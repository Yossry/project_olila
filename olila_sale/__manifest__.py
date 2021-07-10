# -*- coding: utf-8 -*-
{
    'name': "Olila Sales",
    'summary': """Olila Sales""",
    'description': """ Olila Sales """,
    'author': "Preciseways",
    'website': "http://www.preciseways.com",
    'version': '14.0',
    'depends': ['sale_management','stock', 'sale_stock', 'fleet', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/olial_seq.xml',
        'views/res_partner_view.xml',
        'views/sale_view.xml',
        'views/cost_estimation.xml',
        'views/stock_picking.xml',
        'views/request_for_quote_view.xml',
        'views/zone_view.xml',
        'views/product_view.xml',
        'views/hr_employee_view.xml',
    ],
}