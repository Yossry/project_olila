# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api, _
from odoo.exceptions import UserError

class PartialReleaseLetterLine(models.TransientModel):
    _name = "partial.release.letter.line"
    _description = 'Partial Release Letter Line'

    product_id = fields.Many2one("product.product", string='Product')
    quantity = fields.Float(string="Qty", default=1.0)
    item_code = fields.Char(string="Item Code")
    unit_price = fields.Float(string='Unit price')
    wizard_id = fields.Many2one('partial.release.letter.wizard', string='Unit price')
    lc_opning_line_id = fields.Many2one('lc.opening.lines', string="LC Opening Line")

class PartialReleaseLetter(models.TransientModel):
    _name = 'partial.release.letter.wizard'
    _description = 'Partial Release Letter'

    @api.model
    def _prepare_partial_release_lines(self, line):
        quantity = line.quantity - line.partial_qty
        return {
            'product_id': line.product_id.id,
            'quantity': quantity or 0.0,
            'unit_price':line.unit_price,
            'item_code':line.item_code,
            'lc_opning_line_id':line.id,
        }

    @api.model
    def default_get(self, fields_list):
        res = super(PartialReleaseLetter, self).default_get(fields_list)
        opening_id = self.env['lc.opening'].browse(self.env.context.get('active_id'))
        if opening_id:
            lines = [(0, 0, self._prepare_partial_release_lines(line)) for line in opening_id.mapped('lc_opening_lines').filtered(lambda x: x.quantity > x.partial_qty)]
            res.update({'lines_ids': lines, 'lc_opning_id': opening_id and opening_id.id})
        return res

    lines_ids = fields.One2many('partial.release.letter.line', 'wizard_id', string='Lines')
    lc_opning_id = fields.Many2one('lc.opening', string="Opening")

    def _prepare_release_lines(self, line):
        line.lc_opning_line_id.partial_qty += line.quantity
        if line.quantity < 1:
            raise UserError(_('You can not process for zero quantity'))
        return {
            'product_name' : line.product_id.id or False,
            'product_code' : line.item_code,
            'name': line.product_id.name,
            'hs_code': line.product_id.hs_code,
            'quantity': line.quantity,
            'unit_price': line.unit_price,
        }

    def _prepare_release_data(self):
        vals = {}
        lines = [(0, 0, self._prepare_release_lines(line)) for line in self.lines_ids]
        if lines:
            vals = {
                'lc_number': self.lc_opning_id.lc_no,
                'lc_date': self.lc_opning_id.lc_date,
                'lc_open_id': self.lc_opning_id.id,
                'currency_id': self.lc_opning_id.order_id and self.lc_opning_id.order_id.currency_id and self.lc_opning_id.order_id.currency_id.id,
                'product_lines': lines
            }
        return vals

    def create_partial_release(self):
        data = self._prepare_release_data()
        self.env['document.release.letter'].create(data)
        return True
