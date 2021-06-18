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
    'depends': ['olila_fleet','account'],
    'data': [
        'security/distribution_security.xml',
        'security/ir.model.access.csv',
        'data/olila_data.xml',
        'wizard/delivery_report_wizard.xml',
        'views/vehicle_distribution_view.xml',
        'views/driver_view.xml',
        'views/fleet_vehicle.xml',
        'reports/deliver_report_view.xml', 
    ],
}
