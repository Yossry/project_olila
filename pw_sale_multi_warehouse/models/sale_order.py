# -*- coding: utf-8 -*-
from odoo import api, fields, models
from collections import defaultdict

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    warehouse_id = fields.Many2one('stock.warehouse', compute='_compute_warehouse', related=False, store=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, string="Warehouse")

    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        res['warehouse_id'] = self.warehouse_id or self.order_id.warehouse_id
        return res

    @api.depends('order_id.warehouse_id')
    def _compute_warehouse(self):
        for line in self:
            line.warehouse_id = line.order_id.warehouse_id
