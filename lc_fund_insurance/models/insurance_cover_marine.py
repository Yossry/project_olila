from odoo import api, fields, models
from datetime import date, datetime

class InsuranceMarine(models.Model):
    _name = "insurance.cover.marine"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Insurance Details.marine"
    
    
    @api.depends('insurance_marine_ids.price_subtotal', 'insurance_marine_ids.quantity', 'insurance_marine_ids.unit_price', 'total_in_foreign_cr', 'premium_amount')
    def _compute_total(self):
        for rec in self:
            total_amount = 0.0
            premium_amount = 0.0
            premium_amount = rec.premium_amount
            for line in rec.insurance_marine_ids:
                total_amount += line.price_subtotal
            rec.total_in_foreign_cr = total_amount
            rec.total_amount = rec.total_in_foreign_cr + premium_amount

    @api.depends('stamp_duty', 'added', 'war')
    def _compute_marine_total(self):
        for rec in self:
            total_marine = 0.0
            total_marine = rec.stamp_duty + rec.added + rec.war
            rec.total_cost = total_marine


    name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New')
    partner_id = fields.Many2one("res.partner", string="Insurance Company")
    branch_id = fields.Many2one('res.branch', string="Branch")
    zip = fields.Char(change_default=True)
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    note = fields.Text(string="Note")
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    phone = fields.Char(string='Phone', copy=False)
    email   = fields.Char(string="Email",  copy=False)
    fax = fields.Char(string="Fax", copy=False)
    vat_regi_no = fields.Char(string='VAT')
    classs = fields.Char(string="Class")
    marine_cover_no = fields.Char(string='Marine Cover No')
    war = fields.Float(string="War", copy=False)
    stamp_duty = fields.Float(string='Stamp Duty', copy=False)
    added = fields.Float(string="Added", copy=False)
    total_amount = fields.Float(string='Total Amount', compute="_compute_total")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, readonly=True, default=lambda self: self.env.company.currency_id.id)
    insurance_marine_ids = fields.One2many("insurance.cover.marine.lines", "insurance_marine_id", string="Insurance Lines")
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'), ('send','Send'),('amendment', 'Amendment'),('marine','Marine'),('cancel','Cancel')], 
        string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    total_in_foreign_cr = fields.Float(string="Total In (FC)")
    premium_amount = fields.Float(string="Premium Amount")
    classification_code = fields.Float(string="Classification Code")
    total_cost = fields.Float(string="Total Cost", compute="_compute_marine_total")
    commercial_invoice = fields.Char(string="Invoice No")
    commercial_date = fields.Date(string="Invoice Date")
    bl_number = fields.Char(string="BL Number")
    bl_date = fields.Date(string="BL Date")
    policy_number = fields.Char(string="Policy Number")
    policy_date = fields.Date(string="Policy Date")
    insurance_cover_id = fields.Many2one('insurance.cover', string="Insurance Cover")


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.phone = self.partner_id.phone
            self.email = self.partner_id.email
            self.street = self.partner_id.street or ' '
            self.street2 = self.partner_id.street2 or ' '
            self.zip = self.partner_id.zip
            self.city = self.partner_id.city
            self.state_id = self.partner_id.state_id.id
            self.country_id = self.partner_id.country_id.id
            self.vat_regi_no = self.partner_id.vat


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('insurance.cover.marine') or '/'
        return super(InsuranceMarine, self).create(vals)


    def button_confirm(self):
        self.write({'state' : 'confirm'})
        return True

    def button_send(self):
        self.write({'state' : 'send'})
        return True

    def button_cancel(self):
        self.write({'state' : 'cancel'})
        return True

    def button_marine(self):
        self.write({'state' : 'marine'})
        return True

    def button_draft(self):
        self.write({'state' : 'draft'})
        return True

class InsuranceCovearineMarineLines(models.Model):
    _name="insurance.cover.marine.lines"
    _description="Insurance Details"

    @api.depends('unit_price', 'quantity')
    def _compute_amount(self):
        for line in self:
            line.price_subtotal = line.unit_price * line.quantity
 
    insurance_marine_id = fields.Many2one("insurance.cover.marine", string='Insurance marine')
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', 'Item Name', track_visibility='onchange', required=True)
    item_code = fields.Char(string='Item Code')
    hs_code = fields.Char(string="HS Code")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    quantity = fields.Float('Quantity', track_visibility='onchange', default=1.0)
    unit_price = fields.Integer(string='Unit price')
    price_subtotal = fields.Float(string='Subtotal', compute="_compute_amount")

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.standard_price or 0.0
            self.hs_code = self.product_id.hs_code
            self.item_code = self.product_id.default_code
