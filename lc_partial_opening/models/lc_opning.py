# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class LcOpeningLines(models.Model):
    _inherit="lc.opening.lines"

    partial_qty = fields.Float(string="Release Qty")
    picking_qty = fields.Float(string="Picking Qty")

class LCOpning(models.Model):
    _inherit = "lc.opening"

    picking_count = fields.Integer(compute='_picking_count', string='Pickings')

    def _picking_count(self):
        for rec in self:
            picking_ids = self.env['stock.picking'].search([('lc_opning_id', '=', rec.id), ('picking_type_id.code', '=', 'incoming')])
            rec.picking_count = len(picking_ids.ids)

    def open_incoming_picking(self):
        picking_ids = self.env['stock.picking'].search([('lc_opning_id', '=', self.id), ('picking_type_id.code', '=', 'incoming')])
        return {
            'name': _('LC Pickings'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', picking_ids.ids)],
        }

class StockPicking(models.Model):
    _inherit = "stock.picking"

    lc_opning_id = fields.Many2one('lc.opening', string="LC Opening")

class CfAggent(models.Model):
    _inherit = 'res.cf.aggent'

    is_processed = fields.Boolean(string="Processed")

class LcOpeningCharges(models.Model):
    _inherit="lc.charges.line"

    is_processed = fields.Boolean(string="Processed")