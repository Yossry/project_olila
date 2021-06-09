from odoo import api, fields, models, _
from datetime import date, datetime

class LCRequest(models.Model):
    _name="lc.request"
    _description="Lc Request"

    name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New')
    application_date = fields.Date(string="Application Date", default=fields.Date.today())
    purchase_order_no = fields.Many2one("purchase.order",string='Purchase No')
    purchase_order_date = fields.Date(string="Purchase Date")
    currency = fields.Many2one("res.currency") 
    total_amount = fields.Float(string='Total Amount')
    bank_code = fields.Char(string='Bank Code')
    bank_name = fields.Char(string='Bank Name')
    bank_branch = fields.Char(string='Bank Branch')
    bank_address =fields.Char(string='Bank Address')
    account_no = fields.Char(string='Account No')
    lc_type = fields.Selection([('deferred', 'Deferred'), ('cash', 'Cash'),('at_sight','At Sight')], string='LC Type', default='cash')
    lcaf_no = fields.Many2one('lc.opening.fund.requisition', string='LCAF No')
    lc_amount = fields.Float(string="LC Amount")
    margin = fields.Float()
    remarks = fields.Text()
    maturity_balance = fields.Float(string='Maturity Balance')
    opening_count = fields.Integer(compute='_opening_count', string='# Opening')
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('open','Open'),('print','Print'),('cancel','Cancel')], string="State", default='draft', copy=False)

    def _opening_count(self):
        for rec in self:
            request_ids = self.env['lc.opening'].search([('lc_request', '=', rec.id)])
            rec.opening_count = len(request_ids.ids)

    def view_lc_opening(self):
        request_ids = self.env['lc.opening'].search([('lc_request', '=', self.id)])
        return {
            'name': _('LC Opening'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'lc.opening',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', request_ids.ids)],
        }

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lc.request') or ('New')
        return super(LCRequest, self).create(vals)

    def _prepare_lines(self, line):
        return {
            'product_id' : line.product_id.id,
            'item_code' : line.product_id.default_code,
            'quantity' : line.product_qty,
            'unit_price' : line.price_unit
        }

    def create_lc_opening(self):
        vals = {
                'order_id': self.purchase_order_no and self.purchase_order_no.id,
                'po_date' : self.purchase_order_date,
                'currency_id': self.currency and self.currency.id,
                'lc_no': self.lcaf_no and self.lcaf_no.id,
                'lc_amount' : self.lc_amount,
                'lc_date' : self.application_date,
                'bank_name' : self.bank_name,
                'bank_address' : self.bank_address,
                'lc_request': self.id,
                'lc_opening_lines' : [(0,0, self._prepare_lines(line)) for line in self.lcaf_no.requisition_line_ids]
        }
        self.env['lc.opening'].create(vals)

    def button_draft(self):
       self.write({'state': 'draft'})

    def button_confirm(self):
        for rec in self:
            rec.write({'state': 'confirm'})

    def button_cancel(self):
        self.write({'state': 'cancel'})

    def button_open(self):
        for rec in self:
            rec.create_lc_opening()
            if rec.lcaf_no:
                rec.lcaf_no.state = 'open'
            rec.write({'state': 'open'})
