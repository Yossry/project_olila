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

    def _get_new_picking_values(self):
        values = super(StockMove, self)._get_new_picking_values()
        if self.partner_id:
            values.update({'partner_id': self.partner_id.id})
        return values

    def _key_assign_picking(self):
        self.ensure_one()
        return self.group_id, self.location_id, self.partner_id, self.location_dest_id, self.picking_type_id
        
    def _get_domain_search_picking(self):
        domain = [
                ('group_id', '=', self.group_id.id),
                ('location_id', '=', self.location_id.id),
                ('location_dest_id', '=', self.location_dest_id.id),
                ('picking_type_id', '=', self.picking_type_id.id),
                ('printed', '=', False),
                ('partner_id', '=', self.partner_id.id),
                ('immediate_transfer', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])]
        return domain
    
    def _search_picking_for_assignation(self):
        self.ensure_one()
        domain = self._get_domain_search_picking()
        picking = self.env['stock.picking'].search(domain, limit=1)
        return picking


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        datas = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
        if values.get('shipping_partner_id'):
            datas.update({
                'partner_id': values.get('shipping_partner_id') if values.get('shipping_partner_id') else False,

                })
        return datas
