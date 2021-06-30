from odoo import api, fields, models, _
from datetime import date, datetime

class Branch(models.Model):
    _name = "res.branch"
    _description = "Branch Details"

    name = fields.Char()

class Insurance(models.Model):
    _name = "insurance.cover"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Insurance Details"
    
    @api.depends('insurance_ids.price_subtotal', 'insurance_ids.quantity', 'insurance_ids.unit_price', 'total_in_foreign_cr', 'premium_amount')
    def _compute_total(self):
        for rec in self:
            total_amount = 0.0
            premium_amount = 0.0
            premium_amount = rec.premium_amount
            for line in rec.insurance_ids:
                total_amount += line.price_subtotal
            rec.total_in_foreign_cr = total_amount
            rec.total_amount = rec.total_in_foreign_cr + premium_amount

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
    vat_regi_no = fields.Char(string='VAT Registration No')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, readonly=True, default=lambda self: self.env.company.currency_id.id)
    lc_requisition_id = fields.Many2one("lc.opening.fund.requisition")
    insurance_ids = fields.One2many("insurance.cover.lines", "insurance_id", string="Insurance Lines")
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'), ('send','Send'),('marine','Marine'),('cancel','Cancel')], 
        string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    total_amount = fields.Float(string='Total Amount', compute="_compute_total")
    total_in_foreign_cr = fields.Float(string="Total In (FC)", compute="_compute_total")
    premium_amount = fields.Float(string="Premium Amount")
    marine_count = fields.Integer(compute='_marine_count', string='# Marine')

    def _marine_count(self):
        for rec in self:
            marine_ids = self.env['insurance.cover.marine'].search([('insurance_cover_id', '=', rec.id)])
            rec.marine_count = len(marine_ids.ids)

    def view_marine(self):
        marine_ids = self.env['insurance.cover.marine'].search([('insurance_cover_id', '=', self.id)])
        return {
            'name': _('Insurance Marine'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'insurance.cover.marine',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', marine_ids.ids)],
        }

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

    def _prepare_marine_lines(self, line):
        return{
            'product_id' : line.product_id.id or False,
            'item_code' : line.item_code,
            'hs_code' : line.hs_code,
            'country_id' : line.country_id or False,
            'quantity' : line.quantity,
            'unit_price' : line.unit_price,
            'price_subtotal' : line.price_subtotal
        }

    def _prepare_marine_data(self):
        lines = [(0,0, self._prepare_marine_lines(line)) for line in self.insurance_ids]
        return {
            'partner_id' : self.partner_id.id or False,
            'branch_id' : self.branch_id.id or False,
            'insurance_cover_id' : self.id,
            'insurance_marine_ids' : lines or False
        }

    def insurance_cover_marine(self):
        marine_data = self._prepare_marine_data()
        marine_id = self.env['insurance.cover.marine'].create(marine_data)
        marine_id._onchange_partner_id()
        self.state = 'marine'




class InsuranceCoverLines(models.Model):
    _name="insurance.cover.lines"
    _description="Insurance Details"

    @api.depends('unit_price', 'quantity')
    def _compute_amount(self):
        for line in self:
            line.price_subtotal = line.unit_price * line.quantity
 
    insurance_id = fields.Many2one("insurance.cover", string='Insurance')
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
