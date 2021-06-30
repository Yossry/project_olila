{
	
	'name':"Letter of Credit Release Letter",
	'summary':"""Letter of Credit Release Letter""",
	'description':"Letter of Credit Release Letter",
	'category':"Purchase",
	'version':"14.0",
	'depends':['lc_opening_fund_requisition', 'lc_opening'],
	'data':[
			'security/ir.model.access.csv',	
			'views/letter.xml',	
			'data/data.xml',
		],
	'demo':[],
	'application': True,	
}
