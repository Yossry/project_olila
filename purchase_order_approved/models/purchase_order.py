# Copyright 2017 ForgeFlow S.L.

from odoo import fields, models

PURCHASE_REQUISITION_STATES = [
    ('draft', 'Draft'),
    ('ongoing', 'Ongoing'),
    ('in_progress', 'Confirmed'),
    ('open', 'Bid Selection'),
    ('done', 'Closed'),
    ('cancel', 'Cancelled'),
    ('awaiting_approval',"Awaiting Approval"),
	('manager_approved',"Manager Approved"),
]

class PurchaseRequisition(models.Model):
	_inherit = "purchase.requisition"

	state = fields.Selection(PURCHASE_REQUISITION_STATES,'Status', tracking=True, required=True, copy=False, default='draft')
	state_blanket_order = fields.Selection(PURCHASE_REQUISITION_STATES, compute='_set_state')

	def submit_order(self):
		self.write({'state':'awaiting_approval'})
	
	def manager_approval(self):
		self.write({'state':'manager_approved'})

	def action_done(self):
		"""Generate all purchase order based on selected lines, should only be called on one agreement at a time"""
		if any(purchase_order.state in ['draft', 'sent', 'to approve', 'awaiting_approval', 'manager_approved'] for purchase_order in self.mapped('purchase_ids')):
			raise UserError(_('You have to cancel or validate every RfQ before closing the purchase requisition.'))
		for requisition in self:
			for requisition_line in requisition.line_ids:
				requisition_line.supplier_info_ids.unlink()
		self.write({'state': 'done'})

class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	state = fields.Selection(selection_add=[
		('to approve', 'To Approve'),
		('awaiting_approval',"Awaiting Approval"),
		('manager_approved',"Manager Approved"),
		])
	
	def submit_order(self):
		self.write({'state':'awaiting_approval'})
	
	def manager_approval(self):
		self.write({'state':'manager_approved'})
		
	def button_confirm(self):
		for order in self:
			if order.state not in ['draft', 'sent', 'awaiting_approval','manager_approved']:
				continue
			order._add_supplier_to_product()
			# Deal with double validation process
			if order.company_id.po_double_validation == 'one_step'\
					or (order.company_id.po_double_validation == 'two_step'\
						and order.amount_total < self.env.company.currency_id._convert(
							order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
					or order.user_has_groups('purchase.group_purchase_manager'):
				order.button_approve()
			else:
				order.write({'state': 'to approve'})
			if order.partner_id not in order.message_partner_ids:
				order.message_subscribe([order.partner_id.id])
		return True
