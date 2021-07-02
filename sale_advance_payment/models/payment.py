# -*- coding: utf-8 -*-

from odoo import models, fields

class ResBank(models.Model):
	_inherit = "res.bank"

	bank_branch = fields.Char(string="Branch")

class AccountPayment(models.Model):
    _inherit = "account.payment"

    sale_id = fields.Many2one('sale.order', "Sale", readonly=True, states={'draft': [('readonly', False)]})
    dealer = fields.Boolean('Dealer')
    distributor_code = fields.Char()
    bank_branch = fields.Char(string="Branch")
    check_date = fields.Date(string="Check Date")
    check_no = fields.Char(string="Check No")
    file_attachment = fields.Binary("Attachment")
