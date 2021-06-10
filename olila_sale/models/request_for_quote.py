# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

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
    quantity = fields.Float(string="Quantity", default=1.0)
    expected_delivery = fields.Date(string="Expected Delivery Date")
    remarks = fields.Text(string="Remarks")
    note = fields.Text(string="Terms & Condition")

    def action_confirm(self):
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
