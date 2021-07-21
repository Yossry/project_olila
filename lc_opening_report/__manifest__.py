# -*- coding: utf-8 -*-
{
    'name': "LC Request Reports",
    'summary': """LC Opening and Amendment Reports""",
    'version': '14.0',
    'depends': ['lc_ammenment', 'purchase_requisition'],
    'data': [
       	'report/report_extend.xml',
        'report/report_action.xml',
        'report/amendment_report.xml',
        'report/lc_opning_report.xml',
    ],
}