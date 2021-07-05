{
	
	'name':"Edit Purchase Order",
	'summary':"""Edit Purchase Order when rfq is confirmed""",
	'description':"Edit Purchase Order when rfq is confirmed",
	'category':"purchase",
	'version':"14.0",
	'depends':['lc_opening_fund_requisition', 'purchase_request', 'purchase_stock'],
	'data':[
		
		'views/purchase_order_readonly.xml',
		],
	'demo':[],
	'application': True,	
}
