# -*- coding: utf-8 -*-

{
    'name': 'Purchase Discount',
    'version': '14.0.0.0',
    'category': 'purchase',
    'summary': 'This apps help to define a discount per line in the purchase orders.',
    'description': """
        In this module you can add discounts in purchase lines.
        You will get discount on purhcase reports.
        Discounts in Purchase order lines
""",
    'depends': ['base','purchase'],
    'data': [
            'views/purchase.xml',
            'views/inherit_purchase_report.xml'
    ],
    'installable': True,
}


