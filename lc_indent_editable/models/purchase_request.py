from odoo import api, fields, models

class PurchaseRequest(models.Model):
    _inherit="purchase.request"

    is_purchase_rfq = fields.Boolean(string="Is Purchase Confirmed", compute='_is_purchase_order')

    def _is_purchase_order(self):
        for rec in self:
            rec.is_purchase_rfq = False
            requisition_id = self.env['purchase.requisition'].search([('purchase_request_ids', 'in', rec.ids)])
            if requisition_id.purchase_ids:
                rec.is_purchase_rfq = True
