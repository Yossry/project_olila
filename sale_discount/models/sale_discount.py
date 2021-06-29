# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError

visible_states = {
    'draft': [('readonly', False)], 
    'sent': [('readonly', False)], 
    'sale': [('readonly', True)]
}

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_type = fields.Selection([
        ('percentage', 'Percent'),
        ('fixed', 'Fixed')
        ], default='percentage',
        states=visible_states,
        help='''Set the decimal accuracy for discount, it advicable to set to 5 digits.''')
    discount = fields.Monetary('Discount',
        digits=dp.get_precision('discount'), readonly=True, store=True, compute='_compute_total_amount')
    discount_fix = fields.Float('Global Discount', digits=dp.get_precision('discount'),
        readonly=True, states=visible_states)
    discount_per = fields.Float(compute='_compute_total_amount', digits=dp.get_precision('discount'))

    @api.depends('order_line', 'order_line.price_subtotal')
    def _compute_total_amount(self):
        for order in self:
            lineTotalDiscount = sum((line.product_uom_qty * (line.price_unit) - line.price_subtotal) if line.discount_type == 'percentage' else line.discount_fix for line in order.order_line)
            order.discount = lineTotalDiscount
            total_amount = order.amount_untaxed + order.discount
            if total_amount:
                order.discount_per = (order.discount / total_amount) * 100

    def apply_discount(self):
        if self.discount_type == 'percentage':
            if self.discount_fix > 100:
                raise ValidationError(_('Invalid global discount!'))
        for line in self.order_line:
            line.discount_type = self.discount_type
            line_total = line.product_uom_qty * line.price_unit
            if line.discount_type == 'fixed':
                line.discount = (self.discount_fix / line_total) * 100
                line.discount_fix = self.discount_fix
            if line.discount_type == 'percentage':
                line.discount = self.discount_fix
                line.discount_fix = (line_total * line.discount) / 100
            
    @api.onchange('discount_type')
    def onchange_discount(self):
        self.discount_fix = 0.0

    def _prepare_invoice(self):
        invoiceVals = super(SaleOrder, self)._prepare_invoice()
        self.ensure_one()
        invoiceVals.update({
            'total_discount' : self.discount_fix,
            'discount_type': self.discount_type,
            'discount_fix': self.discount_fix,
        })
        return invoiceVals

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # @api.depends('discount')
    # def _compute_fix_discount_amount(self):
    #     for line in self:
    #         line_total = line.product_uom_qty * line.price_unit
    #         if line.tax_id.filtered(lambda x: x.price_include == True):
    #             taxes = line.tax_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_uom_qty,
    #                 product=line.product_id, partner=line.order_id.partner_shipping_id)
    #             line_total = taxes['total_excluded']
    #         if line.order_id.discount_type == 'fixed':
    #             line.discount_fix = line.order_id.discount_fix
    #         if line.order_id.discount_type == 'percentage' and line.order_id.discount_fix <= 100:
    #             line.discount_fix = line_total * (line.order_id.discount_fix / 100)

    discount_type = fields.Selection([
        ('percentage', 'Percent'),
        ('fixed', 'Fixed')
        ], default='percentage', states=visible_states)
    discount_fix = fields.Float('Discount', digits=dp.get_precision('discount'), states=visible_states)

    @api.depends('product_uom_qty', 'discount_fix', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for line in self:
            quantity = 1.0
            price = 0.0
            line_total = line.price_unit * line.product_uom_qty
            if line.discount_type == 'fixed':
                price = line.price_unit * line.product_uom_qty - (line.discount_fix or 0.0)
                line.discount = (line.discount_fix / line_total) * 100
            else:
                line.discount_fix = (line_total * line.discount) / 100
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                quantity = line.product_uom_qty
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, quantity, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update(
            discount_type=self.discount_type,
            discount = self.discount,
            discount_fix=self.discount_fix
        )
        return res
