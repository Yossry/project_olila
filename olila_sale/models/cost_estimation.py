# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta, datetime

class CostEstimation(models.Model):
    _name = 'cost.estimation'
    _description = 'cost estimation'
    _inherit = ['format.address.mixin', 'image.mixin', 'mail.thread', 'mail.activity.mixin']

    @api.depends('estimation_line_ids', 'estimation_line_ids.price_subtotal', 'margin', 'estimation_line_ids.price_unit')
    def _compute_amount_all(self):
        total_estimation = 0.0
        for cost in self:
            for rec in cost.estimation_line_ids:
                total_estimation += rec.price_subtotal
            cost.total_estimation  = total_estimation + cost.margin

    @api.model
    def default_get(self, default_fields):
        res = super(CostEstimation, self).default_get(default_fields)
        return res

    name = fields.Char(string='Name', readonly=True, default="New")
    date = fields.Date(string='Date', default=fields.Date.today())
    note = fields.Text(string='Remarks')
    code = fields.Char('Code', size=256)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    rfq_number = fields.Char(string="RFQ Number")
    order_id = fields.Many2one('sale.order', 'Quotation')
    partner_id = fields.Many2one("res.partner", string="Partner")
    product_id = fields.Many2one('product.product', 'Product')
    description_sale = fields.Char('Description', size=256)
    is_primary_approved = fields.Boolean("Is Primary Approved")
    is_final_approved = fields.Boolean("Is Final Approved")
    quantity = fields.Float("Quantity", default=1)
    state = fields.Selection([('draft','Draft'), ('confirm','Confirm'), ('primary_approved', 'Primary Approved'), ('final_approved', 'Final Approved'), ('accept','Accept'), ('reject','Reject')], 
        string='Status', readonly=True, index=True, copy=False, default='draft')
    margin = fields.Monetary(string="Margin")
    total_estimation = fields.Monetary(string="Final Price", compute="_compute_amount_all")
    rfq_id = fields.Many2one("request.for.quote", "Corporate RFQ")
    rfq_count = fields.Integer(compute='_rfq_count', string='# Requests')
    estimation_line_ids  = fields.One2many('cost.estimation.line', 'estimation_id', string='Estimation Lines')
    responsible = fields.Many2one('hr.employee', string="Responsible", related='partner_id.responsible', store=True, readonly=False)

    def _rfq_count(self):
        for rec in self:
            rfq_ids = self.env['sale.order'].search([('rfq_id', '=', self.id)])
            rec.rfq_count = len(rfq_ids.ids)

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
            Product = self.env['product.product'].sudo()
            self.product_id = Product.create({'name': self.description_sale, 'type': 'product', 'default_code': self.code})
            price_unit = self.total_estimation / self.quantity
            if not self.order_id:
                # Find Order or create one
                self.order_id = self.env['sale.order'].create({
                        'partner_id' : self.partner_id.id,
                        'date_order': datetime.now().date(),
                        'sale_type' : 'corporate_sales',
                        'payment_term_id': self.partner_id.property_payment_term_id.id,
                        'pricelist_id': self.partner_id.property_product_pricelist.id,
                        'zone_id': self.partner_id.zone_id.id,
                        'rfq_id' : self.rfq_id.id,
                    })
            self.order_id.order_line.create({'product_id': self.product_id.id, 'product_uom_qty': self.quantity, 'price_unit': price_unit, 'order_id': self.order_id.id})
            self.write({'state': 'accept'})
            if self.rfq_id:
                self.rfq_id.state = 'done'
        else:
            raise UserError(_('Need to approve before accept cost estimation.'))
        return True

    def open_sales(self):
        sale_order = self.env['sale.order'].search([('rfq_id', '=', self.id)])
        return {
            'name': _('Corporate Sales'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', sale_order.ids)],
        }

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
