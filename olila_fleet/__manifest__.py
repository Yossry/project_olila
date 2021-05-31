# -*- coding: utf-8 -*-
{
    'name': "Transport",
    'summary':'Trnsportation changes related to fleet and inventory',
    'description': 'This module modify fleet',
    'author': "rohitsrivastava99@gmail.com",
    'category': 'fleet',
    'version': '14.0.1',
    'depends': ['fleet','hr'],
    'data': [
        'security/ir.model.access.csv',
        #'data/fleet_tags.xml',
        'data/fleet_history_data.xml',
        'views/fleet_view.xml',
        'views/vehicle_fuel_log.xml',
        'views/vehicle_history.xml',
        'views/liecense_renewal_history.xml',
        'views/fleet_route_plan.xml',
        'views/vehicle_components.xml',
        'views/vehicle_tyre_deatails.xml',
    ],
}
