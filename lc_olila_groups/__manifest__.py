{
    'name' : 'Olila LC Group',
    'version' : '1.0',
    'summary': 'Olila LC group',
    'sequence': 1,
    'description': """Olila group""",
    'depends' : ['lc_ammenment', 'lc_document_letter', 'lc_loan_control'],
    'data': [
        'security/user_security.xml',
        'security/lc_opening_applay_group.xml',
    ],
    'installable': True,
    'application': True,
}
