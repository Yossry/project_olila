# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class LCOpeningFundRequisition(models.Model):
    _name = 'lc.opening.fund.requisition'
    _description = 'Lc Opening Fund Requisition'

    purchase_id = fields.Many2one('purchase.order', string="Purchase No")
    name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New')
    purchase_orde_date = fields.Datetime(string="Purchase Date")
    lc_requisition_date = fields.Date(string="LC Requisition Date")
    supplier_id = fields.Many2one('res.partner', string="Supplier")
    department_id = fields.Many2one('hr.department', string='Department')
    origin = fields.Many2one("res.country", string="Origin")
    lcaf_no = fields.Char(string="LCAF No")
    is_lcaf = fields.Boolean(string="LCAF")
    is_tm = fields.Boolean(string="T/M")
    is_imp = fields.Boolean(string="IMP")
    usd_to_tk = fields.Boolean(string="USD to TK")
    usd_tk_amount = fields.Float(string="Amount")
    state = fields.Selection([('draft','Draft'),('confirm', 'Confirm'),('request','Request'),('open','Open'),('accept', 'Accept'),('amendment', 'Amendment'),('done', 'Done'),('cancel','Cancel')], 
        string='Status', readonly=True, index=True, 
        copy=False, default='draft', track_visibility='onchange')
    margin = fields.Float(string="Margin", copy=False)
    commission = fields.Float(string="Commission", copy=False)
    source_tax= fields.Float(string="Source Tax", copy=False)
    vat_on_commission= fields.Float(string="Vat on Commission", copy=False)
    pt_charge = fields.Float(string="P&T Charge", copy=False) 
    insurance_charge  = fields.Float(string="Insurance Charge", copy=False) 
    remarks = fields.Text(string="Remarks", copy=False) 
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, readonly=True,default=lambda self: self.env.company.currency_id.id)
    requisition_line_ids  = fields.One2many('lc.opening.fund.requisition.line', 'lc_requisition_id', string='Lc Opening Fund Requisition Line')
    cf_aggent_ids  = fields.One2many('res.cf.aggent', 'lc_requisition_id', string='CF Agent')
    charges_ids  = fields.One2many('custom.charges', 'lc_requisition_id', string='Custom Charges')
    insurance_count = fields.Integer(compute='_insurance_count', string='# Landed Cost')
    explosive_count = fields.Integer(compute='_explosive_count', string='# Pre-approvals')
    is_insurance = fields.Boolean(string="Insurance", copy=False)
    pre_appoval = fields.Boolean(string="Pre-Approval", copy=False)

    def _explosive_count(self):
        for rec in self:
            explosive_ids = self.env['approval.explosive'].search([('lc_requisition_id', '=', rec.id)])
            rec.explosive_count = len(explosive_ids.ids)

    def _insurance_count(self):
        for rec in self:
            insurance_ids = self.env['insurance.cover'].search([('lc_requisition_id', '=', rec.id)])
            rec.insurance_count = len(insurance_ids.ids)

    def open_explosive_cost(self):
        explosive_ids = self.env['approval.explosive'].search([('lc_requisition_id', '=', self.id)])
        return {
            'name': _('Approvals Explosive'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'approval.explosive',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', explosive_ids.ids)],
        }

    def open_insurance_cost(self):
        insurance_ids = self.env['insurance.cover'].search([('lc_requisition_id', '=', self.id)])
        return {
            'name': _('Insurance Cover'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'insurance.cover',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', insurance_ids.ids)],
        }

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lc.opening.fund.requisition') or '/'
        return super(LCOpeningFundRequisition, self).create(vals)

    def create_lc_request(self):
        self.write({'state' : 'request'})
        return True

    def button_done(self):
        for rec in self:
            if rec.purchase_id:
                rec.purchase_id.button_approve()
            rec.state = 'done'
        return True

    def button_confirm(self):
        self.write({'state' : 'confirm'})
        return True

    def button_lc_opening(self):
        self.write({'state' : 'open'})
        return True

    def button_make_done(self):
        self.write({'state' : 'done'})
        return True

    def button_cancel(self):
        self.write({'state' : 'cancel'})
        return True

    def _prepare_lines(self, line):
        return {
            'sequence' : line.sequence,
            'product_id' : line.product_id.id,
            'item_code' : line.product_id.default_code,
            'hs_code' : line.product_id.hs_code,
            'quantity' : line.product_qty,
            'unit_price' : line.price_unit
        }

    def _prepare_values(self):
        lines = [(0,0, self._prepare_lines(line)) for line in self.requisition_line_ids]
        return {
        'partner_id' : self.supplier_id.id,
        'lc_requisition_id' : self.id,
        'insurance_ids' : lines
        }

    def create_insurance_cover(self):
        values = self._prepare_values()
        insurance_id = self.env['insurance.cover'].create(values)
        self.is_insurance = True
        return True

    def _prepare_explosive_lines(self, line):
        return {
            'product_id' : line.product_id.id,
            'item_code' : line.product_id.default_code,
            'importable_quantity' : 0.0,
            'stock_before_approval' : 0.0,
            'applic_quantity' : line.product_qty,
            'stock_after_import' : 0.0,
            'arrival_days_required' : 1,
            'factory_stock_report_date' : fields.Date.today(),
            'import_quantity' : 0.0,
            'application_date' : fields.Date.today(),
            'speed_money_am' : line.price_unit
        }

    def _approval_explosive(self):
        lines = [(0,0, self._prepare_explosive_lines(line)) for line in self.requisition_line_ids]
        return {
        'purchase_order_date' : self.purchase_id.date_order if self.purchase_id.date_order else False,
        'purchase_order_no' : self.purchase_id.id if self.purchase_id else False,
        'lc_requisition_id' : self.id,
        'explosive_lines' : lines,
        }

    def create_approval_explosive(self):
        values = self._approval_explosive()
        insurance_id = self.env['approval.explosive'].create(values)
        self.pre_appoval = True
        return True


class LCOpeningFundRequisitionLine(models.Model):
    _name = 'lc.opening.fund.requisition.line'
    _description = 'Lc Opening Fund Requisition Line'

    sequence = fields.Integer(string='Sequence', default=10)
    lc_requisition_id = fields.Many2one('lc.opening.fund.requisition', string="LC Requisition")
    product_id = fields.Many2one('product.product', 'Item Name', track_visibility='onchange', required=True)
    description = fields.Char('Item Code', size=256, track_visibility='onchange')
    hs_code = fields.Char('HS Code', size=256, track_visibility='onchange')
    product_qty = fields.Float('Quantity', track_visibility='onchange', default=1.0)
    price_unit = fields.Float(string='Unit Price', help='Price Unit')
    

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.standard_price or 0.0
            self.hs_code = self.product_id.hs_code
            self.description = self.product_id.display_name

