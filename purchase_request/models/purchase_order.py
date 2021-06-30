# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    department_id = fields.Many2one('hr.department', string='Department')
    lc_type = fields.Selection([('deferred', 'Deferred'), ('cash', 'Cash'),('at_sight','At Sight')], string='LC Type', default='cash')
