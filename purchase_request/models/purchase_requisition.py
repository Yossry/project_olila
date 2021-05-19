# -*- coding: utf-8 -*-

from odoo import models,fields,api, _
from odoo.exceptions import ValidationError


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    purchase_request_id = fields.Many2one('purchase.request', string='Picking Type')
