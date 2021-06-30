# -*- coding: utf-8 -*-
{
    'name': "LC Opening Fund Requisition",
    'summary': """Letter of Credit Opening Fund Requisition""",
    'version': '14.0',
    'depends': ['olila_sale', 'purchase_requisition', 'purchase_stock', 'hr', 'delivery', 'purchase_request', 'l10n_generic_coa'],
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