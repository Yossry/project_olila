# -*- coding: utf-8 -*-
from odoo import models,fields,api
from itertools import groupby

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    shipping_partner_id = fields.Many2one(related='order_id.partner_id', store=True, string='Shipping Customer', readonly=False)

    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        if self.shipping_partner_id:
            values.update({'shipping_partner_id': self.shipping_partner_id.id})
        return values

class StockMove(models.Model):
    _inherit = "stock.move"

    shipping_partner_id = fields.Many2one('res.partner', string="PArtner")

    def _get_new_picking_values(self):
        values = super(StockMove, self)._get_new_picking_values()
        if self.shipping_partner_id:
            values.update({'partner_id': self.shipping_partner_id.id})
        return values

    def _search_picking_for_assignation(self):
        self.ensure_one()
        picking = self.env['stock.picking'].search([
                ('group_id', '=', self.group_id.id),
                ('location_id', '=', self.location_id.id),
                ('location_dest_id', '=', self.location_dest_id.id),
                ('picking_type_id', '=', self.picking_type_id.id),
                ('printed', '=', False),
                ('immediate_transfer', '=', False),
                ('partner_id', '=', self.shipping_partner_id.id),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1)
        return picking

    def _assign_picking(self):
        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a new
        picking to assign them to. """
        Picking = self.env['stock.picking']
        grouped_moves = groupby(sorted(self, key=lambda m: [f.id for f in m._key_assign_picking()]), key=lambda m: [m._key_assign_picking()])
        for group, moves in grouped_moves:
            moves = self.env['stock.move'].concat(*list(moves))
            new_picking = False
            # Could pass the arguments contained in group but they are the same
            # for each move that why moves[0] is acceptable
            for mvs in moves:
                picking = mvs._search_picking_for_assignation()
                if picking:
                    if any(picking.partner_id.id != m.partner_id.id or
                            picking.origin != m.origin for m in moves):
                        # If a picking is found, we'll append `move` to its move list and thus its
                        # `partner_id` and `ref` field will refer to multiple records. In this
                        # case, we chose to  wipe them.
                        picking.write({
                            'partner_id': False,
                            'origin': False,
                        })
                else:
                    new_picking = True
                    picking = Picking.create(mvs._get_new_picking_values())

                mvs.write({'picking_id': picking.id})
                mvs._assign_picking_post_process(new=new_picking)
        return True

class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        datas = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
        if values.get('shipping_partner_id'):
            datas.update({
                'partner_id': values.get('shipping_partner_id') if values.get('shipping_partner_id') else False,
                'shipping_partner_id' : values.get('shipping_partner_id')
                })
        return datas