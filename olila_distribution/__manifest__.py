# -*- coding: utf-8 -*-
{
    'name': "Olila Distribution",
    'summary': 'This module incorporates olila distribution flow with delivery order \
          and internal stock',
    'description': """
       Olila Distribution
       Route Plan
    """,
    'author': "rohitsrivastava99@gmail.com",
    'category': 'stock',
    'version': '0.1',
    'depends': ['olila_fleet'],
    'data': [
        'security/distribution_security.xml',
        'security/ir.model.access.csv',
        'data/olila_data.xml',
        'wizard/delivery_report_wizard.xml',
        'views/vehicle_distribution_view.xml',
        'views/stock_picking_view.xml',
        'reports/deliver_report_view.xml', 
    ],
}
