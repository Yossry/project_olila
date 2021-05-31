# -*- coding: utf-8 -*-
{
    'name': "Olila Return Sales Order",
    'summary': """Olila Return Sales Order""",
    'description': """ Olila Return Sales Order """,
    'version': '14.0',
    'depends': ['sale_management', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/blial_seq.xml',
        # 'views/res_partner_view.xml',
        # 'views/sale_view.xml',
        # 'views/cost_estimation.xml',
        # 'views/stock_picking.xml',
        'wizard/sale_order_wizard_view.xml',
    ],
}