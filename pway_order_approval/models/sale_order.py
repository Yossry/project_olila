# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def submit_for_approval(self):
        for rec in self:
            # Notify user with second approvers on setting activities 
            rec.state = 'waiting_for_approval'

    def submit_for_second_approval(self):
        for rec in self:
            # Notify user to belongs to second approver by seting activity
            rec.state = 'waiting_for_final_approval'

    def approve_sale_order(self):
        res = super(SaleOrder,self).action_confirm()
        return res
            
    
    state = fields.Selection(selection_add=[
        ('waiting_for_approval', 'Waiting For Approval'),
        ('waiting_for_final_approval', 'Final Approval')], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')