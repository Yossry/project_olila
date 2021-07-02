# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleAdvancePayment(models.TransientModel):
    _name = "sale.advance.payment"

    journal_id = fields.Many2one('account.journal', 'Payment Method', required=True)
    amount_to_pay = fields.Monetary(string='Amount', required=True, default=0.0)
    amount_total = fields.Float('Total Amount', readonly=True)
    check_date = fields.Date(string="Check Date")
    check_no = fields.Char(string="Check No")
    currency_id = fields.Many2one("res.currency", "Currency", readonly=True)
    partner_bank_id = fields.Many2one('res.partner.bank', string="Bank Account No")
    bank_branch = fields.Char(string="Branch")
    file_attachment = fields.Binary("Attachment")
    is_bank_journal = fields.Boolean(string="IS Bank")

    @api.onchange('journal_id')
    def OnchangeJournal(self):
      self.is_bank_journal = False
      if self.journal_id.type == 'bank':
        self.is_bank_journal = True


    @api.onchange('partner_bank_id')
    def OnchangePartnerBank(self):
      if self.partner_bank_id and self.partner_bank_id.bank_id.bank_branch:
        self.bank_branch = self.partner_bank_id.bank_id.bank_branch


    def get_paid_amount(self, sale_id):
      amount_to_pay = 0.0
      payments = self.env['account.payment'].search([('sale_id', '=', sale_id.id)])
      if payments:
        amount_to_pay = sum(payments.mapped('amount'))
      return sale_id.amount_untaxed - amount_to_pay

    @api.model
    def default_get(self, fields):
        total_amount = 0.0
        res = super(SaleAdvancePayment, self).default_get(fields)
        sale_id = self.env.context.get('active_id', False)
        if sale_id:
          sale = self.env['sale.order'].browse(sale_id)
          total_amount = self.get_paid_amount(sale)
          res.update({'amount_total': total_amount, 'currency_id': sale.pricelist_id.currency_id.id})
        return res

    @api.constrains('amount_to_pay')
    def _check_valid_payment(self):
      if self.amount_to_pay < 1:
          raise UserError(_("Amount can't be negative or zero !"))
      sale_id = self.env.context.get('active_id', False)
      if sale_id:
        sale = self.env['sale.order'].browse(sale_id)
        if sale and self.amount_to_pay < self.amount_total:
          raise UserError(_("Paid amount must be greater than or equal to sale total !"))

    def make_advance_payment(self):
        sale_id = self.env.context.get('active_id', False)
        if sale_id:
            sale = self.env['sale.order'].browse(sale_id)
            exchange_rate = self.env['res.currency']._get_conversion_rate(sale.company_id.currency_id, sale.currency_id, sale.company_id, sale.date_order)
            currency_amount = self.amount_to_pay * (1.0 / exchange_rate)
            payment_dict = {  'payment_type': 'inbound',
                              'partner_type': 'customer',
                              'sale_id': sale.id,
                              'ref': _("Advance") + " - " + sale.name,
                              'partner_id': sale.partner_id and sale.partner_id.id,
                              'journal_id': self.journal_id and self.journal_id.id,
                              'company_id': sale.company_id and sale.company_id.id,
                              'currency_id': sale.pricelist_id.currency_id and sale.pricelist_id.currency_id.id,
                              'date': sale.date_order,
                              'amount': currency_amount,
                              'check_no': self.check_no,
                              'check_date': self.check_date,
                              'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                              'partner_bank_id' : self.partner_bank_id.id,
                              'bank_branch' : self.partner_bank_id.bank_id.bank_branch,
                              'file_attachment' : self.file_attachment,
                          }
            payment = self.env['account.payment'].create(payment_dict)
        return {'type': 'ir.actions.act_window_close'}
