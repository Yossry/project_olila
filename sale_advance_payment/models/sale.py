# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleOrder(models.Model):
	_inherit = "sale.order"
	
	payment_count = fields.Integer(string='Advance', compute='_compute_payment')
	sale_payment_ids = fields.One2many('account.payment', 'sale_id', string="Advanced Payment", readonly=True)

	def action_view_payment(self):
		pay_records = self.env['account.payment']
		sale_payment_ids = self.mapped('sale_payment_ids')
		pay_records = sale_payment_ids
		return {
		    'name': _('Advance'),
		    'view_type': 'form',
		    'view_mode': 'tree,form',
		    'res_model': 'account.payment',
		    'view_id': False,
		    'type': 'ir.actions.act_window',
		    'domain': [('id', 'in', pay_records.ids)],
		}

	@api.depends('sale_payment_ids', 'invoice_ids', 'invoice_ids.state')
	def _compute_payment(self):
	    for order in self:
	    	pay_records  = order.mapped('sale_payment_ids')
	    	order.payment_count = sum(pay_records.mapped('amount'))

	# def action_confirm(self):
	# 	move_lines = self.env['account.move.line']
	# 	res = super(SaleOrder, self).action_confirm()
	# 	for order in self.filtered(lambda x: x.sale_payment_ids):
	# 		inv_data = order._prepare_invoice()
	# 		invoice_id = self.env['account.invoice'].create(inv_data)
	# 		for line in order.order_line.sorted(key=lambda l:l.qty_to_invoice < 0):
	# 			line.invoice_line_create(invoice_id.id, line.product_uom_qty)
	# 		invoice_id.compute_taxes()
	# 		invoice_id.action_invoice_open()
	# 		invoice_move = invoice_id.mapped('move_id').mapped('line_ids').filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
	# 		payment_move = order.mapped('sale_payment_ids').mapped('move_line_ids').filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
	# 		move_lines |= (invoice_move + payment_move)
	# 		move_lines.auto_reconcile_lines()
	# 	return res