# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CostEstimation(models.Model):
    _name = 'cost.estimation'
    _description = 'cost estimation'

    @api.depends('estimation_line_ids', 'estimation_line_ids.price_subtotal', 'estimation_line_ids.price_unit')
    def _compute_amount_all(self):
        total_estimation = 0.0
        for rec in self.estimation_line_ids:
            total_estimation += rec.price_subtotal
        self.total_estimation  = total_estimation

    @api.model
    def default_get(self, default_fields):
        res = super(CostEstimation, self).default_get(default_fields)
        if self.env.context.get('order_id'):
            res.update({'order_id' : self.env.context.get('order_id')})
        return res

    #name = fields.Char(string='name', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    name = fields.Char(string='Name', readonly=True)
    date = fields.Date(string='Estimation Date')
    note = fields.Text(string='Note')
    state = fields.Selection([('draft','Draft'),('approved','Approved'),('launch','Launch')], 
        string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    total_estimation = fields.Float(string="Total", compute="_compute_amount_all")
    estimation_line_ids  = fields.One2many('cost.estimation.line', 'estimation_id', string='Estimation Lines')
    order_id = fields.Many2one('sale.order', string="Order ID")

    @api.model
    def create(self, values):
        if not values.get('name'):
            values['name'] = self.env['ir.sequence'].next_by_code('cost.estimation')
        return super(CostEstimation, self).create(values)

    def button_approved(self):
        self.write({'state' : 'approved'})
        return True

    def button_launch(self):
        self.write({'state' : 'launch'})
        return True

class CostEstimationLine(models.Model):
    _name = 'cost.estimation.line'
    _description = 'cost estimation line'

    estimation_id = fields.Many2one('cost.estimation', string="Cost Estimation")
    product_id = fields.Many2one('product.product', 'Product', track_visibility='onchange', required=True)
    description = fields.Char('Description', size=256, track_visibility='onchange')
    product_qty = fields.Float('Quantity', track_visibility='onchange', default=1.0)
    product_uom_id = fields.Many2one('uom.uom', string='Product Uom',)
    price_unit = fields.Float(string='Unit Price', help='Price Unit')
    price_subtotal = fields.Float(string='Subtotal', compute="_compute_amount")

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.lst_price or 0.0
            self.product_uom_id = self.product_id.uom_id.id

    @api.depends('product_id', 'product_qty', 'price_unit')
    def _compute_amount(self):
        for rec in self:
            rec.price_subtotal = (rec.product_qty * rec.price_unit)
