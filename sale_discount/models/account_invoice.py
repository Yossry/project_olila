# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    total_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_compute_total_amount', digits=dp.get_precision('Discount'), track_visibility='always')
    discount_type = fields.Selection([
        ('percentage', 'Percent'),
        ('fixed', 'Fixed')
        ], default='percentage', readonly=True, states={'draft': [('readonly', False)]},
        help='''Set the decimal accuracy for discount, it advicable to set to 5 digits.''')
    discount_fix = fields.Float('Global Discount', digits=dp.get_precision('discount'),
        readonly=True, states={'draft': [('readonly', False)]})
    discount_per = fields.Float(compute='_compute_total_amount', digits=dp.get_precision('discount'))

    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice')
    def _compute_total_amount(self):
        for invoice in self:
            lineTotalDiscount = sum((line.quantity * (line.price_unit) - line.price_subtotal) if line.discount_type == 'percentage' else line.discount_fix for line in invoice.invoice_line_ids)
            invoice.total_discount = lineTotalDiscount
            total_amount = invoice.amount_untaxed + invoice.total_discount
            if total_amount:
                invoice.discount_per = (invoice.total_discount / total_amount) * 100

    def apply_discount(self):
        if self.discount_type == 'percentage':
            if self.discount_fix > 100:
                raise ValidationError(_('Invalid global discount!'))
        for line in self.invoice_line_ids:
            line.discount_type = self.discount_type
            line_total = line.quantity * line.price_unit
            if line.discount_type == 'fixed':
                line.discount = (self.discount_fix / line_total) * 100
                line.discount_fix = self.discount_fix
            if line.discount_type == 'percentage':
                line.discount = self.discount_fix
                line.discount_fix = (line_total * line.discount) / 100
        self.compute_taxes()

    @api.onchange('discount_type')
    def onchange_discount(self):
        self.discount_fix = 0.0

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    discount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', 'Percent')
        ], default='percentage', string="Discount Type")
    discount = fields.Float(string='Discount(%)', digits=dp.get_precision('Discount'), default=0.0)
    discount_fix = fields.Float('Discount', digits=dp.get_precision('discount'))

    @api.onchange('discount_type')
    def _onchange_discount_type(self):
        self.discount_fix = 0.0
        self.discount = 0.0

    @api.depends('price_unit', 'discount', 'discount_type', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'discount_fix')
    def _compute_price(self):
        for line in self:
            currency = line.invoice_id and line.invoice_id.currency_id or None
            # subTotalAmount = 0.0
            price = 0.0
            line_total = line.price_unit * line.quantity
            if line.discount_type == 'fixed':
                price = line.price_unit * line.quantity - line.discount_fix or 0.0
                line.discount = (line.discount_fix / line_total) * 100
                # subTotalAmount = price
            if line.discount_type == 'percentage':
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                line.discount_fix = (line_total * line.discount) / 100
                # subTotalAmount = line.quantity * price
            taxes = line.invoice_line_tax_ids.compute_all(price, currency, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            # taxes = False
            # if line.invoice_line_tax_ids:
            #     taxes2 = line.invoice_line_tax_ids.compute_all(price, currency, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
            # line.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else subTotalAmount
            # line.price_total = price_subtotal_signed = taxes['total_included'] if taxes else subTotalAmount
            # if line.invoice_id.currency_id and line.invoice_id.company_id and line.invoice_id.currency_id != line.invoice_id.company_id.currency_id:
            #     price_subtotal_signed = line.invoice_id.currency_id.with_context(date=line.invoice_id.date_invoice).compute(price_subtotal_signed, line.invoice_id.company_id.currency_id)
            # sign = line.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
            # line.price_subtotal_signed = price_subtotal_signed * sign
