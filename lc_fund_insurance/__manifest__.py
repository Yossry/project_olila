{
	
	'name':"Insurance Details",
	'summary':"""Insurance Details""",
	'description':"Insurance Details",
	'category':"Insurance Details",
	'version':"14.0",
	'depends':['base','purchase', 'lc_opening_fund_requisition'],
	'data':[
			'data/ir_sequence.xml',
			'security/ir.model.access.csv',
			'views/insurance.xml',
			'views/explosive_view.xml',

		],
	'demo':[],
	'application': True,	
}
