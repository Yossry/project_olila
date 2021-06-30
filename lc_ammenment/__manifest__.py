{
	
	'name':"Letter of Credit Ammenment",
	'summary':"""Letter of Credit Ammenment""",
	'description':"Letter of Credit Ammenment",
	'category':"Purchase",
	'version':"14.0",
	'depends':['lc_opening_fund_requisition', 'lc_fund_insurance', 'lc_opening'],
	'data':[
			'security/ir.model.access.csv',	
			'views/purchase.xml',		
			'data/data.xml',
		],
	'demo':[],
	'application': True,	
}
