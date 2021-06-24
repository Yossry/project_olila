# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta, datetime

class RequestForQuote(models.Model):
    _name = 'request.for.quote'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Request For Quote'


    name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New')
    state = fields.Selection([('draft','Draft'),('confirm', 'Confirm'),('done', 'Done'),('cancel','Cancel')], 
        string='Status', readonly=True, index=True, 
        copy=False, default='draft', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string="Contact Person")
    date_of_inquiry = fields.Date(string="Date of Inquiry")
    compnay_code = fields.Char(string="Compnay Code")
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
        default=lambda self: self.env.company)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', 
        ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    item_specification = fields.Text(string="Item Specification")
    expected_delivery = fields.Date(string="Expected Delivery Date")
    remarks = fields.Text(string="Remarks")
    note = fields.Text(string="Terms & Condition")
    rfq_count = fields.Integer(compute='_rfq_count', string='# Requests')
    quote_lines = fields.One2many("request.for.quote.line", 'request_quote_id', string="Lines")

    def _rfq_count(self):
        for rec in self:
            rfq_ids = self.env['sale.order'].search([('rfq_id', '=', self.id)])
            rec.rfq_count = len(rfq_ids.ids)

    def open_sale_order(self):
        rfq_ids = self.env['sale.order'].search([('rfq_id', '=', self.id)])
        return {
            'name': _('Corporate Sales'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', rfq_ids.ids)],
        }

    def _prepare_sale_order_line(self, line):
        return {
            'product_id' : line.product_id.id,
            'name' : line.product_id.display_name,
            'product_uom_qty' : line.quantity,
            'price_unit' : line.product_id.list_price
        }

    def create_sale_order(self):
        lines = [(0,0, self._prepare_sale_order_line(line)) for line in self.quote_lines]
        order_id = self.env['sale.order'].create({
                'partner_id' : self.partner_id.id,
                'date_order': datetime.now().date(),
                'sale_type' : 'corporate_sales',
                'rfq_id' : self.id,
                'order_line' : lines
            })
        return True

    def action_confirm(self):
        self.create_sale_order()
        self.write({'state' : 'confirm'})

    def action_done(self):
        self.write({'state' : 'done'})

    def action_cancel(self):
        self.write({'state' : 'cancel'})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('request.for.quote') or '/'
        return super(RequestForQuote, self).create(vals)


class RequestForQuoteLine(models.Model):
    _name = 'request.for.quote.line'
    _description = "Request For Quote"

    product_id = fields.Many2one('product.product', string='Product', track_visibility='onchange', required=True)
    item_code = fields.Char(string="Item Code")
    quantity = fields.Float(string="Quantity", default=1.0)
    request_quote_id = fields.Many2one("request.for.quote", string="Quote id")


    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.item_code = self.product_id.display_name
