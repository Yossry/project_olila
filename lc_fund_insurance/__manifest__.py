{
	
	'name':"Letter of Credit Insurance",
	'summary':""" Letter of Credit Insurance""",
	'description':" Letter of CreditInsurance",
	'category':" Letter of Credit Insurance",
	'version':"14.0",
	'depends':['base','purchase', 'lc_opening_fund_requisition'],
	'data':[
			'data/ir_sequence.xml',
			'security/ir.model.access.csv',
			'views/insurance.xml',
			'views/explosive_view.xml',
			'views/insurance_cover_marine.xml',

		],
	'demo':[],
	'application': True,	
}
