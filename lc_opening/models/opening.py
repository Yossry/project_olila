from odoo import api, fields, models,_
from datetime import date, datetime

class LcOpening(models.Model):
    _name="lc.opening"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description="LC Opening"

    @api.depends('lc_opening_lines.unit_price', 'lc_opening_lines.quantity', 'lc_opening_lines')
    def _compute_total(self):
        total_amount = 0.0
        for rec in self.lc_opening_lines:
            total_amount += rec.total_price
        self.total_amount = total_amount

    def button_confirm(self):
        self.write({'state': 'confirm'})

    def button_accept(self):
        for rec in self:
            if rec.requisition_id:
                rec.requisition_id.state = 'accept'
            rec.write({'state': 'accept'})

    def button_cancel(self):
        self.write({'state': 'cancel'})

    def _move_count(self):
        for rec in self:
            move_ids = self.env['account.move'].search([('opening_id', '=', rec.id)])
            rec.move_count = len(move_ids.ids)

    def view_journal_entry(self):
        move_ids = self.env['account.move'].search([('opening_id', '=', self.id)])
        return {
            'name': _('Journal Entery'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', move_ids.ids)],
        }

    name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New')
    order_id = fields.Many2one("purchase.order",string='Purchase', tracking=True)
    old_purchase_id = fields.Many2one('purchase.order', string='Previous Order', tracking=True)
    po_date = fields.Date(string="PO Date", tracking=True)
    lc_no = fields.Char( string='LC No', tracking=True)
    requisition_id = fields.Many2one('lc.opening.fund.requisition', string='LC Fund Requisition', tracking=True)
    lc_request = fields.Many2one('lc.request', string='LC Request', tracking=True)
    lc_date = fields.Date(string='LC Date', tracking=True)
    lc_amount = fields.Float(string='LC Amount', tracking=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, readonly=True, default=lambda self: self.env.company.currency_id.id)
    shipment_date = fields.Date(string="Shipment Date", tracking=True)
    expire_date = fields.Date(string="Expire date", tracking=True)  
    partial_shipment = fields.Char(string="Partial Shipment", tracking=True)
    port_of_landing  = fields.Char(string="Port of Landing", copy=False, tracking=True) 
    transshipment = fields.Char(string="Transshipment", tracking=True)
    port_of_loading = fields.Char(string="Port of Loading", tracking=True) 
    port_of_destination = fields.Char(string="Port of Destination", tracking=True)
    origin = fields.Many2one("res.country", string="Origin", tracking=True) 
    irc_number = fields.Char(string="IRC Number", tracking=True)
    bin_reg_no = fields.Char(string="BIN Number", tracking=True)
    lcaf_no = fields.Char(string='LCAF No', tracking=True)
    lc_ref_no = fields.Char(string="LC/Sender Ref. No", tracking=True)
    lc_opening_lines = fields.One2many("lc.opening.lines", "opening_id")
    lc_charges_lines = fields.One2many("lc.charges.line", "opening_id")
    cf_aggent_ids = fields.One2many("res.cf.aggent", "opening_id")
    move_count = fields.Integer(compute='_move_count', string='#Move')
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'), ('accept','Accept'), ('amendment','Amendment'), ('cancel','Cancel')], 
        string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    total_amount = fields.Float(string='Total Amount', compute="_compute_total", tracking=True)
    #bank
    bank_name = fields.Char(string="Beneficiary Bank", tracking=True) 
    bank_address = fields.Char(string="Beneficiary Bank Address", tracking=True)
    bank_bin_no = fields.Char(string="Beneficiary Bank BIN Number", tracking=True)
    bank_branch = fields.Char(string="Beneficiary Bank Branch", tracking=True)
    bank_shift_code = fields.Char(string="Beneficiary SWIFT Code", tracking=True)
    beneficiary = fields.Char(string="Beneficiary", tracking=True)

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

    opening_id = fields.Many2one("lc.opening", string='Opening')
    po_line_id = fields.Many2one('purchase.order.line', string="LC Purchase Line")
    product_id = fields.Many2one("product.product", string='Product')
    item_code = fields.Char(string='Item  Code')
    unit_price = fields.Float(string='Unit price')
    quantity = fields.Float(string="Quantity", default=1.0)
    total_price = fields.Float(string="Subtotal", compute='_compute_total_price')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.standard_price or 0.0
            self.item_code = self.product_id.default_code

class LcOpeningCharges(models.Model):
    _name = "lc.charges.line"
    _description="Lc Charges Lines"

    @api.depends('lc_application_charge', 'lc_amendment_charge', 'swift_charge', 'commission', 'stamp', 'vat')
    def _compute_charges_price(self):
        for rec in self:
            rec.total_charges_price = rec.lc_application_charge + rec.lc_amendment_charge + rec.swift_charge + rec.commission + rec.stamp + rec.vat


    lc_application_charge = fields.Float(string="Application Charge")
    lc_amendment_charge = fields.Float(string="Amendment Charge")
    swift_charge = fields.Float(string="Swift Charge")
    commission = fields.Float(string="Commission") 
    stamp = fields.Float(string="Stamp")
    vat = fields.Float(string="Vat")
    opening_id = fields.Many2one("lc.opening", string='Opening')
    total_charges_price = fields.Float(string="Charges Subtotal", compute='_compute_charges_price')