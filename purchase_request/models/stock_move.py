# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = "stock.move"

    request_line_id = fields.Many2one('purchase.request.line', string='Request Line')
