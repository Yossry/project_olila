{
	
	'name':"Letter of Credit Opening",
	'summary':"""Letter of Credit Opening""",
	'description':"Letter of Credit Opening",
	'category':"Letter of Credit Opening",
	'version':"14.0",
	'depends':['lc_opening_fund_requisition', 'lc_fund_insurance'],
	'data':[
		'data/ir_sequence.xml',
		'wizard/lc_opning_journal.xml',
		'security/ir.model.access.csv',	
		'views/lc_opening.xml',
		],
	'demo':[],
	'application': True,	
}
