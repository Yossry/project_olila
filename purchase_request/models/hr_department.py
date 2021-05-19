# -*- coding: utf-8 -*-

from odoo import models,fields,api

class HrDepartment(models.Model):
    _inherit = "hr.department"

    @api.model
    def _get_default_picking_type(self):
        return self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('warehouse_id.company_id', 'in', [self.env.context.get('company_id', self.env.user.company_id.id), False])],
            limit=1).id

    picking_type = fields.Many2one('stock.picking.type', string='Picking Type', default=_get_default_picking_type)
    location_id = fields.Many2one('stock.location', string='Location')
