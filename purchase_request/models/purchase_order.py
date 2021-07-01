# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
    	res = super(PurchaseOrder, self)._onchange_requisition_id()
    	if self.requisition_id:
    		self.origin = self.requisition_id.origin
    		self.remark = self.requisition_id.remark
    		self.department_id = self.requisition_id.department_id and self.requisition_id.department_id.id
    	return res

    department_id = fields.Many2one('hr.department', string='Department')
    remark = fields.Text(string='Remark')
    lc_type = fields.Selection([('deferred', 'Deferred'), ('cash', 'Cash'),('at_sight','At Sight')], string='LC Type', default='cash')
