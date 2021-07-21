from odoo import api, fields, models, _
from datetime import date, datetime

class LcOpening(models.Model):
    _inherit="lc.opening"

    release_count = fields.Integer(compute='_release_count', string='#Ammendments')

    def view_release_letter(self):
        opening_ids = self.env['document.release.letter'].search([('lc_open_id', '=', self.id)])
        return {
            'name': _('Release Letters'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'document.release.letter',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', opening_ids.ids)],
        }

    def _release_count(self):
        for rec in self:
            opening_ids = self.env['document.release.letter'].search([('lc_open_id', '=', rec.id)])
            rec.release_count = len(opening_ids.ids)

    def _prepare_release_lines(self, line):
        return{
            'product_name' : line.product_id.id or False,
            'product_code' : line.item_code,
            'name': line.product_id.name,
            'hs_code': line.product_id.hs_code,
            'quantity': line.quantity,
            'unit_price': line.unit_price,
        }

    def _prepare_release_data(self):
        lines = [(0, 0, self._prepare_release_lines(line)) for line in self.lc_opening_lines]
        return {
            'lc_number': self.lc_no,
            'lc_date': self.lc_date,
            'lc_open_id': self.id,
            'currency_id': self.currency_id and self.currency_id.id,
            'product_lines': lines
        }

    def button_release_letter(self):
        data = self._prepare_release_data()
        self.env['document.release.letter'].create(data)
        return True

class DocumentLetter(models.Model):
    _name = "document.release.letter"
    _description = "Document Details"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New')
    lc_number = fields.Char(string="LC Number")
    lc_date = fields.Char(string="LC Date")
    lc_open_id = fields.Many2one('lc.opening')
    invoice_value = fields.Float(string="Invoice Value")
    bl_number = fields.Char(string="BL Number")
    bl_date = fields.Date(string="BL Date")
    commercial_number = fields.Char(string="Commercial Invoice Number")
    commercial_date  = fields.Date(string="Commercial Invoice Date")
    product_lines = fields.One2many("document.release.letter.line","opening_id")
    margin = fields.Float()  
    commission = fields.Float()
    vat = fields.Float(string="VAT")
    note = fields.Text()
    description = fields.Text()
    postage = fields.Float()
    source_tax = fields.Float(string="Source Tax")
    other_charges = fields.Float(string="Other Charges")
    total_amount = fields.Float(string="Amount in (FC)",compute="compute_amount")
    final_amount = fields.Float(string="Total Amount",compute='_get_sum')
    currency_id = fields.Many2one('res.currency', 'Currency')
    local_currency_id = fields.Many2one('res.currency', 'Currency (BDT)', readonly=True, default=lambda self: self.env.company.currency_id.id)

    state = fields.Selection([('draft','Draft'),('confirm','Confirm'), ('paid','Paid'),('amendment', 'Amendment'),('cancel','Cancel')], 
        string='Status', readonly=True, index=True, copy=False, default='draft')

    def button_paid(self):
        for rec in self:
            rec.write({'state': 'paid'})

    def button_confirm(self):
        for rec in self:
            rec.write({'state': 'confirm'})

    def button_cancel(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('document.release.letter') or '/'
        return super(DocumentLetter, self).create(vals)
        
    @api.depends('margin', 'commission','vat','postage','source_tax' ,'other_charges','total_amount')
    def _get_sum(self):
        for rec in self:
            rec.final_amount = rec.margin+rec.commission +rec.vat +rec.postage + rec.source_tax +rec.other_charges

    @api.depends('product_lines')
    def compute_amount(self):
        total_amount = 0.0
        for order in self:
            for rec in order.product_lines:
                total_amount += rec.total_price
            order.total_amount = total_amount           


class DocumentLetterLine(models.Model):
    _name = "document.release.letter.line"
    _description = "Document Details"

    product_name = fields.Many2one("product.product", string='Product')
    opening_id = fields.Many2one("document.release.letter", string='Opening ID')
    product_code = fields.Char(string='Product Code')
    name = fields.Char(string="Description")
    hs_code = fields.Char(string="HS Code")
    quantity = fields.Float(string="Quantity", required=True, default=1.0)
    unit_price = fields.Float(string='Unit price')
    total_price = fields.Float(string="Subtotal",compute="_total_price") 
    

    @api.onchange('product_name')
    def onchange_product_id(self):
        if self.product_name:
            self.name = self.product_name.display_name
            self.unit_price = self.product_name.standard_price
            self.hs_code = self.product_name.hs_code
            self.product_code = self.product_name.default_code


    @api.depends('quantity','unit_price')
    def _total_price(self):
        for record in self:
            record.total_price = record.quantity * record.unit_price
