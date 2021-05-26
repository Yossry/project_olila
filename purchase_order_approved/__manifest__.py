# Copyright 2017 ForgeFlow S.L.
{
    "name": "Purchase Order Approved",
    "summary": "Add a new state 'Approved' in purchase orders.",
    "version": "14.0.1.0.0",
    "category": "Purchases",
    "installable": True,
    "depends": ['purchase_requisition', 'purchase_stock'],
    "data": ["views/purchase_order_view.xml"],
}
