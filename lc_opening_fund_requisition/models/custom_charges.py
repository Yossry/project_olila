# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CustomCharges(models.Model):
	_name = "custom.charges"
	_description = 'Custom Charges'

	name = fields.Char(string='Name', required=True, readonly=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('custom.charges'))
	bill_of_entry_no = fields.Char(string="Bill of Entry No")
	date = fields.Date(default=fields.Date.today())
	customs_point = fields.Char(string="Customs Point")
	declaration_no = fields.Char(string="Declaration No")
	lc_requisition_id = fields.Many2one('lc.opening.fund.requisition', string="LC Requisition")
	charge_global_ids = fields.One2many('taxes.charge.global', 'charge_id', string='Taxes Charge Global')
	refund_charge_ids = fields.One2many('taxes.refund.charge', 'charge_id', string='Refundable Charge Global')

class TaxesChargeGlobal(models.Model):
	_name = "taxes.charge.global"
	_description = 'taxes.charge.global'

	tax_code = fields.Char(string="Tax Code")
	tax_description = fields.Char(string="Tax Description")
	amount = fields.Float(string="Amount")
	charge_id = fields.Many2one('custom.charges', string="Charges")

class TaxesRefundCharge(models.Model):
	_name = "taxes.refund.charge"
	_description = 'Taxes Refund Charge'

	tax_code = fields.Char(string="Tax Code")
	tax_description = fields.Char(string="Tax Description")
	amount = fields.Float(string="Amount")
	charge_id = fields.Many2one('custom.charges', string="Charges")