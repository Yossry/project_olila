from odoo import api, fields, models


class AccountMove(models.Model):
	_inherit = "account.move"

	opening_id = fields.Many2one("lc.opening", string='Opning')

class Company(models.Model):
	_inherit = "res.company"

	lc_charges_account = fields.Many2one('account.account', string="LC Charges Account")
	lc_agent_charges_account = fields.Many2one('account.account', string="LC Agent Charges Account")
