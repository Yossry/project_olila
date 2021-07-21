# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Company(models.Model):
    _inherit = "res.company"

    account_receivable_id = fields.Many2one('account.account', string="Direct Income Account")
    account_payable_id = fields.Many2one('account.account', string=" Direct Expense Account")


class LCDirectTransfer(models.Model):
    _name = 'lc.direct.transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Direct Transfer'

    name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    payment_type = fields.Selection([('income','Income'), ('expense','Expense')], string='Payment Type', default='income')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    date = fields.Date(string="Date", default=fields.Date.today(), required=True)
    note = fields.Text(string="Notes")
    ref = fields.Char(string="Ref")
    state = fields.Selection([('draft','Draft'), ('confirm','Confirm'), ('paid', 'Paid'), ('cancel','Cancel')], 
        string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')
    line_ids = fields.One2many("lc.direct.transfer.line", "lc_transfer_id")
    move_count = fields.Integer(compute='_move_count', string='#Moves')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lc.direct.transfer') or '/'
        return super(LCDirectTransfer, self).create(vals)

    def button_confirm(self):
        if not self.line_ids:
            raise UserError(_('You need to add some lines before confirm.'))
        self.write({'state' : 'confirm'})

    def button_cancel(self):
        self.write({'state' : 'cancel'})

    def _prepare_move_line(self):
        move_line_dict = []
        company_id = self.env.user.company_id
        partner_id = self.line_ids.mapped('partner_id')
        if self.payment_type == 'income':
            move_line_dict.append({
                'account_id' : company_id.account_receivable_id and company_id.account_receivable_id.id or False,
                'partner_id' : partner_id and partner_id[0].id or False,
                'currency_id' : self.currency_id and self.currency_id.id,
                'name' : self.name,
                'credit' : sum(self.line_ids.mapped('amount')),
                'date_maturity' : self.date,
                'ref': self.name,
                'date': self.date,
            })
        if self.payment_type == 'expense':
            move_line_dict.append({
                'account_id' : company_id.account_payable_id and company_id.account_payable_id.id or False,
                'partner_id' : partner_id and partner_id[0].id or False,
                'currency_id' : self.currency_id and self.currency_id.id,
                'name' : self.name,
                'debit' : sum(self.line_ids.mapped('amount')),
                'date_maturity' : self.date,
                'ref' : self.name,
                'date' : self.date,
            })
        
        for line in self.line_ids:
            if self.payment_type == 'income':
                move_line_dict.append({
                    'account_id' : line.account_id and line.account_id.id or False,
                    'partner_id' : line.partner_id and line.partner_id.id or False,
                    'currency_id' : line.currency_id and line.currency_id.id,
                    'name' : line.ref,
                    'debit' : line.amount,
                    'date_maturity' : self.date,
                    'ref' : line.ref,
                    'date' : self.date,
                })
            if self.payment_type == 'expense':
                move_line_dict.append({
                    'account_id' : line.account_id and line.account_id.id or False,
                    'partner_id' : line.partner_id and line.partner_id.id or False,
                    'name' : line.ref,
                    'currency_id' : line.currency_id and line.currency_id.id,
                    'credit' : line.amount,
                    'date_maturity' : self.date,
                    'ref' : line.ref,
                    'date' : self.date,
                })
        return move_line_dict

    def button_post(self):
        move_line_dict = self._prepare_move_line()
        vals = {
            'move_type' : 'entry',
            'currency_id' : self.currency_id.id or False,
            'date' : self.date,
            'journal_id' : self.journal_id.id or False,
            'lc_treansfer_id' : self.id,
            'narration' : self.note,
            'line_ids': [(0, 0, line_data) for line_data in move_line_dict]            
        }
        move_id = self.env['account.move'].create(vals)
        move_id.ref = self.ref
        self.write({'state' : 'paid'})

    def _move_count(self):
        for rec in self:
            move_ids = self.env['account.move'].search([('lc_treansfer_id', '=', rec.id)])
            rec.move_count = len(move_ids.ids)

    def view_journal_entry(self):
        move_ids = self.env['account.move'].search([('lc_treansfer_id', '=', self.id)])
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', move_ids.ids)],
        }

class DirecTransferLine(models.Model):
    _name = 'lc.direct.transfer.line'
    _description = 'Direct Transfer Line'

    def get_default_account(self):
        journal_ids = self.env['account.journal'].search([('type', 'in', ['cash','bank'])])
        accounts = journal_ids.mapped('default_account_id')
        return accounts

    ref = fields.Char(string="Reference")
    lc_transfer_id = fields.Many2one('lc.direct.transfer', string="Transfer")
    account_ids = fields.Many2many('account.account', default=get_default_account)
    partner_id = fields.Many2one('res.partner', string="Partner")
    account_id = fields.Many2one('account.account', string='Account')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    amount = fields.Float(string="Amount")