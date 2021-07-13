# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api, _
from odoo import exceptions

class AmmendmentWizard(models.TransientModel):
    _name = "ammendment.wizard"

    type = fields.Selection([
        ('major', 'Major'),
        ('minor', 'Minor'),
    ], default='minor')

    def all_state_amendment(self, opening_id):
        for rec in opening_id:
            insurance_cover_ids = self.env['insurance.cover'].search([('lc_requisition_id', '=', rec.requisition_id.id)])
            rec.order_id.state = 'amendment'
            rec.requisition_id.state = 'amendment'
            rec.lc_request.state = 'amendment'
            insurance_cover_ids.write({'state' : 'amendment'})
            if insurance_cover_ids:
                marine_ids = self.env['insurance.cover.marine'].search([('insurance_cover_id', 'in', insurance_cover_ids.ids)])
                marine_ids.write({'state' : 'amendment'})
            explosive_ids = self.env['approval.explosive'].search([('lc_requisition_id', '=', rec.requisition_id.id)])
            if explosive_ids:
                explosive_ids.write({'state' : 'amendment'})
            post_explosive_ids = self.env['post.approval.explosive'].search([('lc_requisition_id', '=', rec.requisition_id.id)])
            if post_explosive_ids:
                post_explosive_ids.write({'state' : 'amendment'})

    def create_amendment_rec(self):
        opening_id = self.env['lc.opening'].browse(self.env.context.get('active_id'))
        if opening_id:
            vals = {
                'purchase_order_no': opening_id.order_id and opening_id.order_id.id,
                'purchase_order_date': opening_id.po_date,
                'lc_no': opening_id.id,
                'amment_type': self.type,
                'requisition_id': opening_id.requisition_id and opening_id.requisition_id.id,
            }
            ammendment_id = self.env['purchase.lc.ammendment'].create(vals)
            if ammendment_id:
                opening_id.state = 'amendment'
            if self.type == 'major':
                self.all_state_amendment(opening_id)
        return True

    def create_ammendment(self):
        self.create_amendment_rec()
        return True