from odoo import api, fields, models,_
from datetime import date, datetime

class LCOpeningFundRequisition(models.Model):
    _inherit = 'lc.opening.fund.requisition'

    ammendment_count = fields.Integer(compute='_ammendment_count', string='#Ammendments')

    def view_fund_ammendment(self):
        opening_ids = self.env['purchase.lc.ammendment'].search([('requisition_id', '=', self.id)])
        return {
            'name': _('Ammendments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.lc.ammendment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', opening_ids.ids)],
        }

    def _ammendment_count(self):
        for rec in self:
            opening_ids = self.env['purchase.lc.ammendment'].search([('requisition_id', '=', rec.id)])
            rec.ammendment_count = len(opening_ids.ids)

class LCOpening(models.Model):
    _inherit="lc.opening"

    ammendment_count = fields.Integer(compute='_ammendment_count', string='#Ammendments')

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

    def _ammendment_count(self):
        for rec in self:
            opening_ids = self.env['purchase.lc.ammendment'].search([('lc_no', '=', rec.id)])
            rec.ammendment_count = len(opening_ids.ids)

    def create_amendment_rec(self):
        for rec in self:
            vals = {
                'purchase_order_no': rec.order_id and rec.order_id.id,
                'purchase_order_date': rec.po_date,
                'lc_no': rec.id,
                'requisition_id': rec.requisition_id and rec.requisition_id.id,
            }
            self.env['purchase.lc.ammendment'].create(vals)

    def button_ammendment(self):
        for rec in self:
            if rec.requisition_id:
                rec.requisition_id.state = 'amendment'
            rec.create_amendment_rec()
        self.write({'state': 'amendment'})

class PurchaseLcAmmendment(models.Model):
    _name="purchase.lc.ammendment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description="Purchase Ammendment"

    report_data = "July 19 2021"  \
                    "The Deputy General Manager"  \
                    "(Foreign Exchange Department)"  \
                    "Sonali Bank Ltd " \
                    "Subject : Prayer for amendment of L/C no. Dated 19.07.2021 for"  \
                    "$0.0 A/c: Olila Glass Industries Ltd. "  \
                    "Dear Sir," \
                    "With Refrance To the above we would like to inform you that we need amendment of the above mentioned L/C as under," \
                    "1. Field no 31D: Now to be read date of expiry on insted or existing" \
                    "1. Field no 44C: Now to be read latest date of Shipment on insted or existing" \
                    "All other terms and condition will remain unchanged." \
                    "Please debit required charges from CD amount NO. to amendment of above L/C" \
                    "We therefore, request you to please arrange to amend as above of the mentioning L/C at your earliest for importing row "\
                    "materials to meet the production schedule smothly" \
                    "Your kind cooperation in this respect will be highly appreciated." \
                    "Thank You" \
                    "Your truly" \
                    "(Admin)" \
                    "Managing Director" \

    name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New')
    amment_type = fields.Selection([('major', 'Major'),('minor', 'Minor')], string='Type', default='minor')
    purchase_order_no = fields.Many2one("purchase.order", string='Purchase Order No')
    purchase_order_date = fields.Date(string="Purchase Order Date")
    lc_no = fields.Many2one('lc.opening', string='LC Opening')
    requisition_id = fields.Many2one('lc.opening.fund.requisition', string='Requisition')
    mur = fields.Char(string="MUR")
    description = fields.Text(default=report_data)
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
    ammendment_charges = fields.Float(string="Charges")
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

    def button_confirm(self):
        self.write({'state' : 'confirm'})

    def button_cancel(self):
        self.write({'state' : 'cancel'})




