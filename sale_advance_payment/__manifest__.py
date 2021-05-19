# -*- coding: utf-8 -*-

{
    "name": "Sale Register Payment",
    "version": "11.0",
    "category": "Sales",
    "description": """Allow to add payments on sales and then use its on invoices""",
    "depends": ["sale", "account"],
    "data": [	"security/ir.model.access.csv",
    			"wizard/sale_advance_payment_wzd_view.xml",
             	"views/sale_view.xml",

             ],
    "installable": True,
}
