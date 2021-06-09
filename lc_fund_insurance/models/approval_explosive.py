
from odoo import api, fields, models

class PreApprovalExplosive(models.Model):
    _name = "approval.explosive"
    _description = "Insurance Details"

    name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New') 
    pre_approval_date = fields.Date(string="Approval Date", copy=False)
    purchase_order_no = fields.Many2one('purchase.order', string='Purchase No', copy=False)
    purchase_order_date = fields.Datetime(string='Purchase order Date', copy=False)
    institute_name = fields.Char(string="Institute Name", copy=False)
    lc_no = fields.Char(string="LC No")
    zip = fields.Char(change_default=True)
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    state = fields.Selection([('draft','Draft'), ('confirm','Confirm'), ('approve','Approve'), ('re_approval','Re Approval'), ('done','Done'), ('cancel','Cancel')], 
        string='Status', readonly=True, index=True, 
        copy=False, default='draft', track_visibility='onchange')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    remark = fields.Text(string="Remark", copy=False)
    explosive_lines = fields.One2many("approval.explosive.line", 'approval_explosive_id', string="Lines")
    commercial_invoice = fields.Char(string="Commercial Invoice")
    packing_list = fields.Char(string="Packing List")
    bill_of_lading  =  fields.Char(string="Bill Of Lading")
    certificate_of_origin = fields.Char(string="Certificate Of Origin")   
    arrival_date = fields.Char(string="Arrival Date")
    lc_requisition_id = fields.Many2one("lc.opening.fund.requisition")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('approval.explosive') or '/'
        return super(PreApprovalExplosive, self).create(vals)


    @api.onchange('state_id')
    def onchange_state_id(self):
        for record in self:
            if record.state_id:
                record.country_id = record.state_id.country_id or False
            else:
                record.country_id = False

    def button_confirm(self):
        self.write({'state' : 'confirm'})

    def button_approve(self):
        self.write({'state' : 'approve'})

    def button_re_approval(self):
        self.write({'state' : 're_approval'})

    def button_cancel(self):
        self.write({'state' : 'cancel'})

    def button_done(self):
        self.write({'state' : 'done'})
    

class PreApprovalExplosiveLine(models.Model):
    _name="approval.explosive.line"
    _description="approval.explosive.line"

    approval_explosive_id = fields.Many2one("approval.explosive", string='Approval Explosive')
    product_id = fields.Many2one('product.product', 'Item', track_visibility='onchange', required=True)
    item_code = fields.Char(string='Item Code')
    importable_quantity = fields.Float(string='Importable Qty')
    stock_before_approval = fields.Float(string='Stock Before Approval')
    applic_quantity = fields.Float(string='Qty')
    stock_after_import =fields.Float(string='Stock After Import')
    arrival_days_required = fields.Integer(string='Arrival Days Required')
    factory_stock_report_date = fields.Date(string='Report Date')
    import_quantity = fields.Float(string='Import Qty')  
    application_no = fields.Char(string='Application No')
    application_date = fields.Date(string='Application Date')
    speed_money_am = fields.Float(string='Amount')