from odoo import api, fields, models
from datetime import date, datetime

class PurchaseLcAmmendment(models.Model):
    _name="purchase.lc.ammendment"
    _description="Purchase Ammendment"

    name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New')
    purchase_order_no = fields.Many2one("purchase.order",string='Purchase Order No')
    purchase_order_date = fields.Date(string="Purchase Order Date")
    lc_no = fields.Many2one('lc.opening', string='LC Opening')
    mur = fields.Char(string="MUR")
    swift_input = fields.Char(string="Swift Input")
    sender_name = fields.Char(string="Sender Name")
    sender_branch = fields.Char(string="Sender Branch")
    sender_address = fields.Char(string="Sender Address")
    receiver_name = fields.Char(string="Receiver Name")
    receiver_branch = fields.Char(string="Receiver Name")
    receiver_address = fields.Char(string="Receiver Address")
    sequence_of_total = fields.Boolean(string="Seq of Total")
    sender_ref_no = fields.Char(string="Sender Reference No")
    bank_ref_no = fields.Char(string="Issuing Bank Ref No")
    bank_code = fields.Char(string="Issuing Bank Code")
    date_issue = fields.Date(string="Issuing Bank Code")
    number_of_amendants = fields.Integer(string="Number of Amendants",default=1)
    date_of_amendant = fields.Date(string="Date of Amendant", default=fields.Date.today())
    purpose_message = fields.Text(string="Purpose Message") 
    from_of_credit = fields.Char(string="From of Documentary Credit")
    application_rules = fields.Text(string="Application Rules")
    date_of_entry = fields.Date(string="Date of Entry")
    place_of_entry = fields.Char(string="Place of Entry")
    last_date_of_shipment = fields.Date(string="Last Date of Shipment")
    information = fields.Text(string="Sender to Receiver Information")
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'), ('cancel','Cancel')], 
        string='Status', readonly=True, index=True, copy=False, default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.lc.ammendment') or ('New')
        return super(PurchaseLcAmmendment, self).create(vals)



