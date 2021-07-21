# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api, _
from odoo.exceptions import UserError

class PartialPickingLine(models.TransientModel):
	_name = "partial.picking.line"
	_description = 'Partial Picking'

	product_id = fields.Many2one("product.product", string='Product')
	quantity = fields.Float(string="Quantity", default=1.0)
	item_code = fields.Char(string="Item Code")
	unit_price = fields.Float(string='Unit Price')
	wizard_id = fields.Many2one('partial.picking.wizard', string='Wizard')
	lc_opning_line_id = fields.Many2one('lc.opening.lines', string="LC Opening Line")
	po_line_id = fields.Many2one('purchase.order.line', string="LC Purchase Line")


class PartialPicking(models.TransientModel):
	_name = 'partial.picking.wizard'
	_description = 'Partial Picking Line'

	lines_ids = fields.One2many('partial.picking.line', 'wizard_id', string='Lines')
	lc_opning_id = fields.Many2one('lc.opening', string="Opening")

	@api.model
	def _prepare_partial_picking_lines(self, line):
		quantity = line.quantity - line.picking_qty
		vals = {
				'product_id': line.product_id.id,
				'quantity': quantity,
				'unit_price': line.unit_price,
				'item_code': line.item_code,
				'lc_opning_line_id': line.id,
				'po_line_id': line.po_line_id.id,
			}
		return vals

	@api.model
	def default_get(self, fields_list):
		lines = []
		res = super(PartialPicking, self).default_get(fields_list)
		opening_id = self.env['lc.opening'].browse(self.env.context.get('active_id'))
		if opening_id:
			for line in opening_id.mapped('lc_opening_lines').filtered(lambda x: x.quantity > x.picking_qty):
				move_ids = self.env['stock.move'].search([('purchase_line_id', '=', line.po_line_id.id), ('picking_code', '=', 'incoming')])
				move_qty = sum(move_ids.mapped('product_uom_qty'))
				po_line_qty = line.po_line_id.product_qty
				if po_line_qty and move_qty and po_line_qty <= move_qty:
					continue
				lines.append([0, 0, self._prepare_partial_picking_lines(line)])
			res.update({'lines_ids': lines, 'lc_opning_id': opening_id and opening_id.id})
		return res

	def _prepare_procurement_id(self):
		procurement = self.env["procurement.group"].create({'name' : self.lc_opning_id.name})
		return procurement

	def _prepare_move_incoming(self):
		moves = []
		company_id = self.env.company
		procurement_id = self._prepare_procurement_id()
		if not self.lines_ids:
			raise UserError(_('You can not process without lines'))
		for line in self.lines_ids:
			if line.quantity < 1:
				raise UserError(_('You can not process for zero quantity'))
			moves.append({
				'name' : self.lc_opning_id.name,
				'product_id': line.product_id and line.product_id.id,
				'product_uom': line.product_id.uom_id and line.product_id.uom_id.id,
				'location_id': self.lc_opning_id.order_id and self.lc_opning_id.order_id.partner_id and self.lc_opning_id.order_id.partner_id.property_stock_supplier.id,
				'location_dest_id': self.lc_opning_id.order_id.picking_type_id and self.lc_opning_id.order_id.picking_type_id.default_location_dest_id.id,
				'company_id': company_id and company_id.id,
				'product_uom_qty': line.quantity,
				'quantity_done': line.quantity,
				'origin': self.lc_opning_id and self.lc_opning_id.name,
				'group_id' : procurement_id and procurement_id.id,
				'picking_type_id': self.lc_opning_id.order_id and self.lc_opning_id.order_id.picking_type_id and self.lc_opning_id.order_id.picking_type_id.id,
				'purchase_line_id': line.po_line_id and line.po_line_id.id,
				'procure_method': 'make_to_stock',
			})
			line.lc_opning_line_id.picking_qty += line.quantity
		return moves

	def create_partial_picking(self):
		move_lines = self._prepare_move_incoming()
		if move_lines:
			move_ids = self.env['stock.move'].create(move_lines)
			if move_ids:
				stock_move = move_ids._action_confirm()
				if stock_move:
					stock_move.picking_id.purchase_id = self.lc_opning_id.order_id and self.lc_opning_id.order_id.id
					stock_move.picking_id.lc_opning_id = self.lc_opning_id and self.lc_opning_id.id
					stock_move._action_done()
		return True
