# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

    is_agent = fields.Boolean(string="Agent")

class CfAggent(models.Model):
    _name = 'res.cf.aggent'
    _description = 'CF Aggent'

    @api.depends('agents_charge_ids.sub_total', 'agents_charge_ids.port_bill', 'agents_charge_ids.shipping_bill', 'agents_charge_ids.labour_bill', 'agents_charge_ids')
    def _compute_total_charge(self):
        total_amount = 0.0
        for rec in self:
            for line in rec.agents_charge_ids:
                total_amount = line.sub_total
            self.total_charge = self.total_charge + total_amount

    name = fields.Char(string='Name', required=True, readonly=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('res.cf.aggent'))
    date = fields.Date(string="Date")
    be_date = fields.Date(string="BE Date")
    be_no = fields.Char(string="BE No")
    product_id = fields.Many2one('product.product', string="Product", required=True)
    item_code = fields.Char(string="Item Code")
    containers_details = fields.Char(string="Containers Details")
    net_weight = fields.Float(string="Net Weight")
    delivery_type = fields.Selection([('normal','Normal'),('advance','Advance')], string='Delivery Type', copy=False, default='normal')
    opening_id = fields.Many2one('lc.opening', string="LC Opening")
    attachment_ids = fields.One2many('ir.attachment', 'cf_aggent_id', string='Attachments')
    agents_charge_ids = fields.One2many('agents.charge', 'cf_aggent_id', string='Agents Charge')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, readonly=True, default=lambda self: self.env.company.currency_id.id)
    total_charge = fields.Float(string="Total", compute="_compute_total_charge")

class IRattachment(models.Model):
    _inherit = "ir.attachment"

    cf_aggent_id = fields.Many2one('res.cf.aggent', string="Agent")

class AgentsCharge(models.Model):
    _name = "agents.charge"
    _description = "agents charge"

    @api.depends('custom_duty', 'port_bill', 'shipping_bill', 'labour_bill')
    def _compute_subtotal(self):
        for line in self:
            line.sub_total = line.custom_duty + line.port_bill + line.shipping_bill + line.labour_bill

    user_id = fields.Many2one('res.partner', string="Charge Head", required=True)
    details = fields.Char(string="Details", copy=False)
    # amount = fields.Float(string="Amount", copy=False)
    custom_duty = fields.Float(string="Custom Duty")
    port_bill = fields.Float(string="Port Bill")
    shipping_bill = fields.Float(string="Shipping Bill")
    labour_bill = fields.Float(string="Labour Bill")
    sub_total = fields.Float(string="Subtotal", compute="_compute_subtotal")
    cf_aggent_id = fields.Many2one('res.cf.aggent', string="Agent")


