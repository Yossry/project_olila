# -*- coding: utf-8 -*-
{
    'name': "LC Opening Fund Requisition",
    'summary': """LC Opening Fund Requisition""",
    'version': '14.0',
    'depends': ['purchase_requisition', 'purchase_stock', 'hr', 'delivery', 'purchase_request'],
    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'views/lc_opening_fund_requisition.xml',
        'views/purchase_view.xml',
        'views/lc_request.xml',
        'report/report_action.xml',
        'report/report_template.xml',
    ],
}