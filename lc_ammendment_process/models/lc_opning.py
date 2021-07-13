# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class LcOpening(models.Model):
	_inherit = 'lc.opening'

	previous_order_total = fields.Float(string="Previous Order Total")

class LCOpeningFundRequisition(models.Model):
	_inherit = 'lc.opening.fund.requisition'

	previous_order_total = fields.Float(string="Previous Order Total")

	def _prepare_request_data(self):
		res = super(LCOpeningFundRequisition, self)._prepare_request_data()
		if self.old_purchase_id:
			res.update(previous_order_total = self.old_purchase_id.amount_total)
		return res

class LCRequest(models.Model):
	_inherit="lc.request"

	previous_order_total = fields.Float(string="Previous Order Total")

	def _prepare_opening_data(self):
		res = super(LCRequest, self)._prepare_opening_data()
		if self.old_purchase_id:
			res.update(previous_order_total = self.old_purchase_id.amount_total)
		return res

class Purchase(models.Model):
	_inherit = 'purchase.order'

	def _prepare_values(self):
		res = super(Purchase, self)._prepare_values()
		if self.old_purchase_id:
			res.update(previous_order_total = self.old_purchase_id.amount_total)
		return res