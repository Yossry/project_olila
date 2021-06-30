# -*- coding: utf-8 -*-
{
    'name': "Letter of Credit Loan",
    'summary': """Letter of Credit Loan""",
    'version': '14.0',
    'depends': ['lc_opening_fund_requisition', 'lc_fund_insurance'],
    'data': [
    	'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'views/loan_control.xml',
    ],
}