# -*- coding: utf-8 -*-
from odoo import models, fields, api

class LoanControl(models.Model):
    _name = 'loan.control'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Loan Control'
    _rec_name = 'number'

    number = fields.Char('Number', required=True, index=True, readonly=True, copy=False, default='New')
    facility_size = fields.Float(string='Facility Size')
    interest_rate = fields.Float(string="Interest Rate")
    tenure = fields.Float(string="Tuner")
    payments_per_year = fields.Float(string="Payments per Year")
    instalment_size = fields.Float(string="Instalment Size")
    due_date = fields.Date(string="Due Date")
    payment_balance = fields.Float(string="Payment  Balance")
    overdue_status = fields.Selection([('active','Active'),('de_activate','DeActivate')], 
        string='Overdue Type', copy=False, default='active')
    state = fields.Selection([('draft','Draft'), ('confirm','Confirm'), ('cancel','Cancel')], 
        string='Status', readonly=True, index=True, 
        copy=False, default='draft', track_visibility='onchange')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['number'] = self.env['ir.sequence'].next_by_code('loan.control') or '/'
        return super(LoanControl, self).create(vals)

    def button_confirm(self):
        self.write({'state' : 'confirm'})

    def button_cancel(self):
        self.write({'state' : 'cancel'})