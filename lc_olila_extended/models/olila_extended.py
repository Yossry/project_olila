# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        res = super(PurchaseRequisitionLine, self)._prepare_purchase_order_line(name, product_qty, price_unit, taxes_ids)
        if self.product_id.hs_code:
        	res.update(hs_code = self.product_id.hs_code)
        return res

class LCOpeningFundRequisition(models.Model):
    _inherit = 'lc.opening.fund.requisition'

    @api.onchange('purchase_id')
    def _onchangePurchaseOrder(self):
    	if self.purchase_id:
    		self.write({'supplier_id' : self.purchase_id.partner_id.id, 'department_id' : self.purchase_id.department_id.id if self.purchase_id.department_id else False,
    			'purchase_order_date' : self.purchase_id.date_order,})

class PurchaseRequest(models.Model):
	_inherit='purchase.request'

	@api.onchange('user_id')
	def _onchangePurchaseOrder(self):
		if self.user_id:
			employee_id = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)], limit=1)
			self.department_id = employee_id.department_id.id if employee_id and employee_id.department_id else False


class Insurance(models.Model):
    _inherit = "insurance.cover"

    @api.depends('insurance_ids.price_subtotal', 'insurance_ids.quantity', 'insurance_ids.unit_price', 'total_in_foreign_cr', 'premium_amount')
    def _compute_total(self):
        for rec in self:
            total_amount = 0.0
            premium_amount = 0.0
            premium_amount = rec.premium_amount
            for line in rec.insurance_ids:
                total_amount += line.price_subtotal
            to_currency = self.env.company.currency_id
            from_currency = rec.lc_requisition_id.purchase_id and rec.lc_requisition_id.purchase_id.currency_id
            amount = self.env['res.currency']._compute(from_currency, to_currency, total_amount, round=True)
            rec.total_in_foreign_cr = amount
            from_amount =  rec.total_in_foreign_cr + premium_amount
            rec.total_amount = from_amount