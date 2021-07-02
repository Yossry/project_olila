# -*- coding: utf-8 -*-
from odoo import api, fields, models
from collections import defaultdict

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    warehouse_id = fields.Many2one(related="order_id.warehouse_id", readonly=False, store=True, string="Warehouse")

    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        res['warehouse_id'] = self.warehouse_id or self.order_id.warehouse_id
        return res


