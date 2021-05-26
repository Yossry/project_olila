# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CostEstimation(models.Model):
    _name = 'cost.estimation'
    _description = 'cost estimation'
    _inherit = ['format.address.mixin', 'image.mixin', 'mail.thread', 'mail.activity.mixin']

    @api.depends('estimation_line_ids', 'estimation_line_ids.price_subtotal', 'estimation_line_ids.price_unit')
    def _compute_amount_all(self):
        total_estimation = 0.0
        for cost in self:
            for rec in cost.estimation_line_ids:
                total_estimation += rec.price_subtotal
            cost.total_estimation  = total_estimation

    @api.model
    def default_get(self, default_fields):
        res = super(CostEstimation, self).default_get(default_fields)
        return res

    name = fields.Char(string='Name', readonly=True, default="New")
    date = fields.Date(string='Date', default=fields.Date.today())
    note = fields.Text(string='Remarks')
    code = fields.Char('Code', size=256)
    rfq_number = fields.Char(string="RFQ Number")
    #selection_product = fields.Selection([('create_new', 'Create New Product'), ('use_existing', 'Use Existing Product')])
    order_id = fields.Many2one('sale.order', 'Quotation')
    product_id = fields.Many2one('product.product', 'Product')
    description_sale = fields.Char('Description', size=256)
    is_primary_approved = fields.Boolean("Is Primary Approved")
    is_final_approved = fields.Boolean("Is Final Approved")
    quantity = fields.Float("Quantity")
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('primary_approved', 'Primary Approved'),('final_approved','Final Approved'), ('accept','Accept'), ('reject','Reject')], 
        string='Status', readonly=True, index=True, copy=False, default='draft')
    total_estimation = fields.Float(string="Final Price", compute="_compute_amount_all")
    estimation_line_ids  = fields.One2many('cost.estimation.line', 'estimation_id', string='Estimation Lines')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.code = self.product_id.default_code
            self.description_sale = self.product_id.description_sale

    @api.model
    def create(self, values):
        if not values.get('name') or values.get('name') == 'New':
            values['name'] = self.env['ir.sequence'].next_by_code('cost.estimation')
        return super(CostEstimation, self).create(values)

    def button_first_approved(self):
        self.write({'state': 'primary_approved', 'is_primary_approved': True})
        return True

    def button_reset_draft(self):
        self.write({'state': 'draft', 'is_primary_approved': False, 'is_final_approved': False})
        return True

    def button_sec_approved(self):
        self.write({'state': 'final_approved', 'is_final_approved': True})
        return True

    def button_accept(self):
        if self.is_final_approved:
            Product = self.env['product.product']
            self.product_id = Product.create({'name': self.description_sale, 'default_code': self.code})
            self.order_id.order_line.create({'product_id': self.product_id.id, 'product_uom_qty': self.quantity, 'order_id': self.order_id.id})
            self.write({'state': 'accept'})
        else:
            raise UserError(_('Need to approve before accept cost estimation.'))
        return True

    def button_confirm(self):
        self.write({'state': 'confirm'})
        return True

    def button_cancel(self):
        self.write({'state': 'reject'})
        return True

class CostEstimationLine(models.Model):
    _name = 'cost.estimation.line'
    _description = 'cost estimation line'

    estimation_id = fields.Many2one('cost.estimation', string="Cost Estimation")
    product_id = fields.Many2one('product.product', 'Product', required=True)
    description = fields.Char('Description', size=256)
    product_qty = fields.Float('Qty', default=1.0)
    product_uom_id = fields.Many2one('uom.uom', string='Uom',)
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
