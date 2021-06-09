from odoo import api, fields, models,_
from datetime import date, datetime

class LcOpening(models.Model):
    _name="lc.opening"
    _description="LC Opening"

    def button_confirm(self):
        self.write({'state': 'confirm'})

    def button_accept(self):
        for rec in self:
            if rec.lc_no:
                rec.lc_no.state = 'accept'
            rec.write({'state': 'accept'})

    def create_amendment_rec(self):
        for rec in self:
            vals = {
                'purchase_order_no': self.order_id and self.order_id.id,
                'purchase_order_date': self.po_date,
                'lc_no': self.id,
            }
            self.env['purchase.lc.ammendment'].create(vals)

    def button_ammendment(self):
        for rec in self:
            if rec.lc_no:
                rec.lc_no.state = 'amendment'
            rec.create_amendment_rec()
        self.write({'state': 'amendment'})

    def button_cancel(self):
        self.write({'state': 'cancel'})

    def _ammendment_count(self):
        for rec in self:
            opening_ids = self.env['purchase.lc.ammendment'].search([('lc_no', '=', rec.id)])
            print("<<<<OPEN>>>>>", opening_ids)
            rec.ammendment_count = len(opening_ids.ids)

    def view_lc_opening_ammendment(self):
        opening_ids = self.env['purchase.lc.ammendment'].search([('lc_no', '=', self.id)])
        return {
            'name': _('Ammendments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.lc.ammendment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', opening_ids.ids)],
        }

    name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New')
    order_id = fields.Many2one("purchase.order",string='Purchase')
    po_date = fields.Date(string="PO Date")
    lc_no = fields.Many2one('lc.opening.fund.requisition', string='LC No')
    lc_request = fields.Many2one('lc.request', string='LC Request')
    lc_date = fields.Date(string='LC Date')
    lc_amount = fields.Float(string='LC Amount')
    currency_id = fields.Many2one('res.currency', 'Currency')
    shipment_date = fields.Date(string="Shipment Date")
    expire_date = fields.Date(string="Expire date")  
    bank_name = fields.Char(string="Bank Name") 
    bank_address = fields.Char(string="Bank Address")
    bank_bin_no = fields.Char(string="Bank Bin No") 
    beneficiary = fields.Char(string="Beneficiary")
    partial_shipment = fields.Char(string="Partial Shipment")    
    transshipment = fields.Char(string="Transshipment")
    port_of_loading = fields.Char(string="Port of Loading") 
    port_of_destination = fields.Char(string="Port of Destination")
    origin = fields.Many2one("res.country", string="Origin") 
    irc_number = fields.Char(string="IRC Number")
    bin_reg_no = fields.Char(string="BIN/VAT Reg No")
    lcaf_no = fields.Char(string='LCAF No')
    lc_ref_no = fields.Char(string="LC/Sender Ref. No")
    lc_opening_lines = fields.One2many("lc.opening.lines", "opening_id")
    lc_charges_lines = fields.One2many("lc.charges.line", "opening_id")
    ammendment_count = fields.Integer(compute='_ammendment_count', string='#Ammendments')
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'), ('accept','Accept'), ('amendment','Amendment'), ('cancel','Cancel')], 
        string='Status', readonly=True, index=True, copy=False, default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lc.opening') or '/'
        return super(LcOpening, self).create(vals)

class LcOpeningLines(models.Model):
    _name="lc.opening.lines"
    _description="Lc Opening Lines"

    @api.depends('quantity', 'unit_price')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = rec.unit_price * rec.quantity

    opening_id = fields.Many2one("lc.opening", string='Opning')
    product_id = fields.Many2one("product.product", string='Product')
    item_code = fields.Char(string='Item  Code')
    unit_price = fields.Float(string='Unit price')
    quantity = fields.Float(string="Quantity", default=1.0)
    total_price = fields.Float(string="Total Price", compute='_compute_total_price')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.standard_price or 0.0
            self.item_code = self.product_id.default_code

class LcOpeningCharges(models.Model):
    _name = "lc.charges.line"
    _description="Lc Charges Lines"

    lc_application_charge = fields.Float(string="Application Charge")
    lc_amendment_charge = fields.Float(string="Amendment Charge")
    swift_charge = fields.Float(string="Swift Charge")
    commission = fields.Float(string="Commission") 
    stamp = fields.Float(string="Stamp")
    vat = fields.Float(string="Vat")
    opening_id = fields.Many2one("lc.opening", string='Opening')