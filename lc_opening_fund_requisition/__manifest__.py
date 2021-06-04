# -*- coding: utf-8 -*-
{
    'name': "LC Opening Fund Requisition",
    'summary': """LC Opening Fund Requisition""",
    'version': '14.0',
    'depends': ['purchase_requisition', 'hr', 'delivery'],
    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'views/lc_opening_fund_requisition.xml',
        'views/purchase_view.xml',
        #'views/cf_aggent_view.xml',
        # 'views/cost_estimation.xml',
        # 'views/stock_picking.xml',
    ],
}