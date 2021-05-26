# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def submit_for_approval(self):
        for rec in self:
            rec.state = 'waiting_for_approval'

    def approve_sale_order(self):
        #for rec in self:
            #rec.action_confirm()
            #rec.state = 'sale'
        res = super(SaleOrder,self).action_confirm()
        return res
            
    
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('waiting_for_approval', 'Waiting For Approval'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')