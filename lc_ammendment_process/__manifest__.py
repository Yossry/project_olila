# -*- coding: utf-8 -*-
{
    'name': "Full LC Ammenment",
    'summary': """LC Major and Minor Ammenment """,
    'version': '1.0',
    'depends': ['lc_opening_fund_requisition', 'lc_ammenment'],
    'data': [
    	'security/ir.model.access.csv',
        'wizard/ammendment_view.xml',
        'views/lc_opning_view.xml',
    ],
}