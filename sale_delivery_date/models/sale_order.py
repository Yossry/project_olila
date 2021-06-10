# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, date, timedelta

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    dispatch_date = fields.Date(string="Delivery Date", compute="_compute_dispatch_date", store=True)

    @api.depends('product_id', 'product_id.sale_delay', 'move_ids', 'customer_lead')
    def _compute_dispatch_date(self):
        for rec in self:
            if not rec.move_ids:
                lead_date = fields.Date.today() + timedelta(days=int(rec.customer_lead))
                rec.dispatch_date = lead_date if lead_date else fields.Date.today()
            else:
                move_id = rec.move_ids.filtered(lambda line: line.state not in ('done', 'cancel'))
                rec.dispatch_date = move_id.date_deadline.date() if move_id else rec.move_ids[0].date_deadline.date()
