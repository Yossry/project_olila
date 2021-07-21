# -*- coding: utf-8 -*-
from odoo import models, fields, api

class LCOpeningFundRequisition(models.Model):
    _inherit = 'lc.opening.fund.requisition'

    def button_cancel(self):
        for rec in self:
            insurance_cover_ids = self.env['insurance.cover'].search([('lc_requisition_id', '=', rec.id)])
            if insurance_cover_ids:
                marine_ids = self.env['insurance.cover.marine'].search([('insurance_cover_id', 'in', insurance_cover_ids.ids)])
            lc_opening_ids = self.env['lc.opening'].search([('requisition_id', '=', rec.id)])
            request_id = self.env['lc.request'].search([('requisition_id', '=', rec.id)])
            explosive_ids = self.env['approval.explosive'].search([('lc_requisition_id', '=', rec.id)])
            post_explosive_ids = self.env['post.approval.explosive'].search([('lc_requisition_id', '=', rec.id)])
            ammendment_ids = self.env['purchase.lc.ammendment'].search([('purchase_order_no', '=', rec.purchase_id.id)])
            request_id.button_cancel()
            lc_opening_ids.button_cancel()
            insurance_cover_ids.button_cancel()
            marine_ids.button_cancel()
            explosive_ids.button_cancel()
            post_explosive_ids.button_cancel()
            ammendment_ids.button_cancel()
            rec.purchase_id.button_cancel()
        return super(LCOpeningFundRequisition, self).button_cancel()