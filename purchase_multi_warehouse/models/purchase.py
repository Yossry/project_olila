# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def _default_warehouse_id(self):
        return self.env.user._get_default_warehouse_id()

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        default=_default_warehouse_id)

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        res = super(PurchaseOrderLine, self)._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        if self.warehouse_id:
        	res['warehouse_id'] = self.warehouse_id.id
        return res

    def _get_warehouse_picking(self, warehouse_id):
        moves = self.picking_ids.mapped('move_lines').filtered(lambda x: x.warehouse_id == warehouse_id)
        return moves.mapped('picking_id').filtered(lambda x: x.state not in ('done', 'cancel'))

    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if any(product.type in ['product', 'consu'] for product in order.order_line.product_id):
                order = order.with_company(order.company_id)
                warehouse_ids = order.order_line.mapped('warehouse_id')
                if warehouse_ids:
                    for warehouse in warehouse_ids:
                        pickings = order._get_warehouse_picking(warehouse)
                        if not pickings:
                            res = order._prepare_picking()
                            res['picking_type_id'] = warehouse.in_type_id.id
                            res['company_id'] = warehouse.company_id.id
                            res['location_dest_id'] = warehouse.in_type_id.default_location_dest_id.id
                            picking = StockPicking.with_user(SUPERUSER_ID).create(res)
                        else:
                            picking = pickings[0]
                        moves = order.order_line.filtered(lambda x: x.warehouse_id == warehouse)._create_stock_moves(picking)
                        moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                        seq = 0
                        for move in sorted(moves, key=lambda move: move.date):
                            seq += 5
                            move.sequence = seq
                        moves._action_assign()
                        picking.message_post_with_view('mail.message_origin_link',
                            values={'self': picking, 'origin': order},
                            subtype_id=self.env.ref('mail.mt_note').id)
                else:
                    pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                    if not pickings:
                        res = order._prepare_picking()
                        picking = StockPicking.with_user(SUPERUSER_ID).create(res)
                    else:
                        picking = pickings[0]
                    moves = order.order_line._create_stock_moves(picking)
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in sorted(moves, key=lambda move: move.date):
                        seq += 5
                        move.sequence = seq
                    moves._action_assign()
                    picking.message_post_with_view('mail.message_origin_link',
                        values={'self': picking, 'origin': order},
                        subtype_id=self.env.ref('mail.mt_note').id)
        return True
