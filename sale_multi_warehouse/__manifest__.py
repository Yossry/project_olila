# -*- coding: utf-8 -*-
{
    'name': 'Sale Multi Delivery by Warehouse',
    'version': '13.0',
    'author': 'jignesh@test.com',
    "category": "Warehouse",
    "depends": ['sale_stock', 'sale_management'],
    'summary': 'Sale multi warehouse | Different Warehouse on sale orderline | Sale Order multiple warehouse | Deliver product from multiple warehouses set warehouse on sale order line ',
    'description': """Sale Order Picking Warehouse Multiple Warehouse on sale order line ship from multiple warehouse outgoing shipment
    """,
    'data': [
    'views/sale_view.xml'],
    'price': 10.0,
    'currency': "EUR",
    "images":["static/description/Banner.png"],
    'application': True,
    'installable': True,
}
