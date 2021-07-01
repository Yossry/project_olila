# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CfAggent(models.Model):
    _name = 'res.cf.aggent'
    _description = 'CF Aggent'

    name = fields.Char(string='Name', required=True, readonly=True, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('res.cf.aggent'))
    date = fields.Date(string="Date")
    be_date = fields.Date(string="BE Date")
    be_no = fields.Char(string="BE No")
    notes = fields.Char()
    product_id = fields.Many2one('product.product', string="Product")
    item_code = fields.Char(string="Item Code")
    containers_details = fields.Char(string="Containers Details")
    net_weight = fields.Float(string="Net Weight")
    delivery_type = fields.Selection([('normal','Normal'),('advance','Advance')], 
        string='Delivery Type', copy=False, default='normal')
    lc_requisition_id = fields.Many2one('lc.opening.fund.requisition', string="LC Requisition")
    attachment_ids = fields.One2many('ir.attachment', 'cf_aggent_id', string='Attachments')
    agents_charge_ids = fields.One2many('agents.charge', 'cf_aggent_id', string='Agents Charge')

class IRattachment(models.Model):
	_inherit = "ir.attachment"

	cf_aggent_id = fields.Many2one('res.cf.aggent', string="Agent")

class AgentsCharge(models.Model):
	_name = "agents.charge"
	_description = "agents charge"

	user_id = fields.Many2one('res.users', string="User")
	details = fields.Char(string="Details", copy=False)
	amount = fields.Float(string="Amount", copy=False)
	total_amount = fields.Float(string="Total", copy=False)
	cf_aggent_id = fields.Many2one('res.cf.aggent', string="Agent")
