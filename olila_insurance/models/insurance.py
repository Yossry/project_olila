from odoo import api, fields, models
from datetime import date, datetime

class Branch(models.Model):
    _name = "res.branch"
    _description = "Branch Details"

    name = fields.Char()

class Insurance(models.Model):
    _name = "insurance.cover"
    _description = "Insurance Details"
    
    def _compute_total(self):
        total = 0.0
        for rec in self:
            for line in rec.insurance_ids:
                total += line.unit_price
            rec.total_amount = total

    name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New') 
    partner_id = fields.Many2one("res.partner", string="Insurance Company", required=True)
    branch_id = fields.Many2one('res.branch', string="Branch")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'), ('send','Send'),('marine','Marine'),('cancel','Cancel')], 
        string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    phone = fields.Char(string='Phone', copy=False)
    email   = fields.Char(string="Email",  copy=False)
    fax = fields.Char(string="Fax", copy=False)
    id_no = fields.Char(string='ID No', copy=False)
    vat_regi_no = fields.Char(string='VAT Registration No')
    marine_cover_no = fields.Char(string='Marine Cover No')
    marine_cover_details = fields.Text(string='Marine Cover Note Details')
    classs = fields.Char(string="Class")
    marine = fields.Float(string="Marine")
    war = fields.Float(string="War", copy=False)
    vat = fields.Char(string="Vat", copy=False)
    stamp_duty = fields.Float(string='Stamp Duty', copy=False)
    added = fields.Float(string="Added", copy=False)
    total_amount = fields.Float(string='Total Amount', compute="_compute_total")
    note = fields.Text(string="Note")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, readonly=True, default=lambda self: self.env.company.currency_id.id)
    lc_requisition_id = fields.Many2one("lc.opening.fund.requisition")
    insurance_ids = fields.One2many("insurance.cover.lines", "insurance_id", string="Insurance Lines")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('insurance.cover') or '/'
        return super(Insurance, self).create(vals)


    @api.onchange('state_id')
    def onchange_state_id(self):
        for record in self:
            if record.state_id:
                record.country_id = record.state_id.country_id or False
            else:
                record.country_id = False

    @api.onchange('country_id')
    def onchange_cont_id(self):
        state_ids = []
        if self.country_id:
            return {'domain': {'state_id': [('country_id', '=', self.country_id.id)]}}
        else:
            return {'domain': {'state_id': []}}

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

class InsuranceCoverLines(models.Model):
    _name="insurance.cover.lines"
    _description="Insurance Details"
 
    insurance_id = fields.Many2one("insurance.cover", string='Insurance')
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', 'Item Name', track_visibility='onchange', required=True)
    item_code = fields.Char(string='Item Code')
    hs_code = fields.Char(string="HS Code")
    quantity = fields.Float('Quantity', track_visibility='onchange', default=1.0)
    unit_price = fields.Integer(string='Unit price')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.standard_price or 0.0
            self.hs_code = self.product_id.hs_code
            self.item_code = self.product_id.default_code
