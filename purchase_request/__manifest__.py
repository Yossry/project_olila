# -*- coding: utf-8 -*-
{
    'name' : 'Purchase Request',
    'summary': 'Purchase Request',
    'sequence': 1,
    'description': """ Purchase Request """,
    'depends': ['hr', 'stock', 'purchase', 'purchase_requisition_stock'],
    'data': [
        'data/purchase_request_data.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/purchase_request_view.xml',
        'views/hr_department_view.xml',
        'views/purchase_order_view.xml',
        'report/purchase_request_report.xml',
        'wizard/purchase_request_wizard_view.xml',
        'wizard/merge_tender_view.xml',
    ],
    'installable': True,
    'application': True,
}