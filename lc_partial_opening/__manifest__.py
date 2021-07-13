# -*- coding: utf-8 -*-
{
    'name': "Partial LC Opening",
    'summary': """Partial LC Opening""",
    'version': '14.0',
    'depends': ['lc_opening_fund_requisition', 'lc_document_letter'],
    'data': [
    	'security/ir.model.access.csv',
        'wizard/partial_release_letter.xml',
        'wizard/partial_picking_view.xml',
        'views/lc_opning_view.xml',
    ],
}