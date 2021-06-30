# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class LCOpeningFundRequisition(models.Model):
    _name = 'lc.opening.fund.requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Lc Opening Fund Requisition'

    @api.depends('requisition_line_ids')
    def _compute_foreign_total(self): 
        for rec in self:
            foreign_total = 0.0
            for line in rec.requisition_line_ids:
                foreign_total += line.sub_total
            rec.lc_foreign_total = foreign_total

    @api.depends('lc_foreign_total', 'conversion_rate')
    def _compute_lc_total(self):
        for rec in self:
            foreign_rate = self.currency_id._get_conversion_rate(self.currency_id, self.bdt_currency_id, self.env.company, fields.Date.context_today(self))
            rate = self.conversion_rate/foreign_rate
            final_total = rec.lc_foreign_total * rate
            rec.lc_fund_total = final_total

    @api.depends('lc_fund_total','margin','commission','source_tax','vat_on_commission','pt_charge','insurance_charge')
    def _compute_total(self): 
        for rec in self:
            lc_total_amount = rec.lc_fund_total + rec.margin + rec.commission + rec.source_tax + rec.vat_on_commission + rec.pt_charge + rec.insurance_charge
            # lc_currency_total = self.bdt_currency_id._convert(lc_total_amount, self.bdt_currency_id, self.currency_id, fields.Date.context_today(self))
            rec.lc_total = lc_total_amount



    pi_number = fields.Char()
    pi_date  = fields.Date()
    purchase_id = fields.Many2one('purchase.order', string="Purchase No")
    name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New')
    purchase_order_date = fields.Datetime(string="Purchase Date")
    lc_requisition_date = fields.Date(string="LC Requisition Date")
    supplier_id = fields.Many2one('res.partner', string="Supplier")
    department_id = fields.Many2one('hr.department', string='Department')
    origin = fields.Many2one("res.country", string="Origin")
    lcaf_no = fields.Char(string="LCAF No")
    is_lcaf = fields.Boolean(string="LCAF")
    is_tm = fields.Boolean(string="T/M")
    is_imp = fields.Boolean(string="IMP")
    imp_amount = fields.Float(string="IMP Amount")
    state = fields.Selection([('draft','Draft'),('confirm', 'Confirm'),('request','Request'),('open','Open'),('accept', 'Accept'),('amendment', 'Amendment'),('done', 'Done'),('cancel','Cancel')], 
        string='Status', readonly=True, index=True, copy=False, default='draft')
    margin = fields.Float(string="Margin", copy=False)
    commission = fields.Float(string="Commission", copy=False)
    source_tax= fields.Float(string="Source Tax", copy=False)
    vat_on_commission= fields.Float(string="Vat on Commission", copy=False)
    pt_charge = fields.Float(string="P&T Charge", copy=False) 
    insurance_charge  = fields.Float(string="Insurance Charge", copy=False) 
    remarks = fields.Text(string="Remarks", copy=False) 
    currency_id = fields.Many2one('res.currency', 'Currency')
    bdt_currency_id = fields.Many2one('res.currency', 'Currency (BDT)', readonly=True, default=lambda self: self.env.company.currency_id.id)
    requisition_line_ids  = fields.One2many('lc.opening.fund.requisition.line', 'lc_requisition_id', string='Lc Opening Fund Requisition Line')
    charges_ids  = fields.One2many('custom.charges', 'lc_requisition_id', string='Custom Charges')
    insurance_count = fields.Integer(compute='_insurance_count', string='# Insurances')
    explosive_count = fields.Integer(compute='_explosive_count', string='# Approvals')
    request_count = fields.Integer(compute='_lc_request_count', string='# Requests')
    opening_count = fields.Integer(compute='_opening_count', string='# Opening')
    picking_count = fields.Integer(compute='_picking_count', string='# Pickings')
    is_insurance = fields.Boolean(string="Insurance", copy=False)
    pre_appoval = fields.Boolean(string="Approval", copy=False)
    lc_request = fields.Boolean(string="Request", copy=False)
    picking = fields.Boolean(string="Picking")
    conversion_rate = fields.Float()
    lc_fund_total = fields.Float(string="BDT Total", compute='_compute_lc_total', store=True)
    lc_foreign_total = fields.Float(string="Foreign Total", compute='_compute_foreign_total', store=True)
    lc_total = fields.Float(string="Total", compute='_compute_total') 

    def _explosive_count(self):
        for rec in self:
            explosive_ids = self.env['approval.explosive'].search([('lc_requisition_id', '=', rec.id)])
            rec.explosive_count = len(explosive_ids.ids)

    def _insurance_count(self):
        for rec in self:
            insurance_ids = self.env['insurance.cover'].search([('lc_requisition_id', '=', rec.id)])
            rec.insurance_count = len(insurance_ids.ids)

    def _lc_request_count(self):
        for rec in self:
            lc_request_ids = self.env['lc.request'].search([('requisition_id', '=', self.id)])
            rec.request_count = len(lc_request_ids.ids)

    def _picking_count(self):
        for rec in self:
            rec.picking_count = len(rec.purchase_id.picking_ids.ids)

    def _opening_count(self):
        for rec in self:
            opening_ids = self.env['lc.opening'].search([('requisition_id', '=', rec.id)])
            rec.opening_count = len(opening_ids.ids)

    def view_lc_opening(self):
        opening_ids = self.env['lc.opening'].search([('requisition_id', '=', self.id)])
        return {
            'name': _('Opening'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'lc.opening',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', opening_ids.ids)],
        }

    def open_explosive_cost(self):
        explosive_ids = self.env['approval.explosive'].search([('lc_requisition_id', '=', self.id)])
        return {
            'name': _('Approval For Explosive'),
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

    def open_lc_request(self):
        lc_request_ids = self.env['lc.request'].search([('requisition_id', '=', self.id)])
        return {
            'name': _('LC Opening Request'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'lc.request',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', lc_request_ids.ids)],
        }

    def open_picking(self):
        return {
            'name': _('Pickings'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.purchase_id.picking_ids.ids)],
        }

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('lc.opening.fund.requisition') or 'New'
        return super(LCOpeningFundRequisition, self).create(vals)

    def button_done(self):
        for rec in self:
            if rec.purchase_id:
                rec.purchase_id.with_context(is_lc=True).button_approve()
            rec.write({'picking': True, 'state': 'done'})
        return True

    def button_confirm(self):
        self.write({'state': 'confirm'})
        return True

    def button_lc_opening(self):
        self.write({'state': 'open'})
        return True

    def button_make_done(self):
        self.write({'state': 'done'})
        return True

    def button_cancel(self):
        self.write({'state': 'cancel'})
        return True

    def button_draft(self):
        self.write({'state': 'draft'})

    def button_create_charges(self):
        return True

    def create_lc_request(self):
        values = self._prepare_request_data()
        self.env['lc.request'].create(values)
        self.write({'lc_request': True, 'state': 'request'})
        return True

    def _prepare_request_data(self):
        return {
            'purchase_order_no': self.purchase_id and self.purchase_id.id,
            'purchase_order_date': self.purchase_order_date,
            'requisition_id': self.id,
            'lcaf_no' : self.lcaf_no,
            'lc_amount': self.lc_total
        }

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
            'lc_requisition_id' : self.id,
            'insurance_ids' : lines
        }

    def create_insurance_cover(self):
        lines = [(0,0, self._prepare_lines(line)) for line in self.requisition_line_ids.filtered(lambda x: x.product_id and x.product_id.material_type != 'sodium_nitrate')]
        self.is_insurance = True
        return {
            'name': _('Insurance Cover'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'insurance.cover',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {
                'default_lc_requisition_id' : self.id,
                'default_insurance_ids': lines
            },
        }

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
        lines = [(0,0, self._prepare_explosive_lines(line)) for line in self.requisition_line_ids.filtered(lambda x: x.product_id and x.product_id.material_type == 'sodium_nitrate')]
        return {
            'purchase_order_date' : self.purchase_id.date_order if self.purchase_id.date_order else False,
            'purchase_order_no' : self.purchase_id.id if self.purchase_id else False,
            'lc_requisition_id' : self.id,
            'explosive_lines' : lines,
        }

    def create_approval_explosive(self):
        values = self._approval_explosive()
        self.env['approval.explosive'].create(values)
        self.pre_appoval = True
        return True


class LCOpeningFundRequisitionLine(models.Model):
    _name = 'lc.opening.fund.requisition.line'
    _description = 'Lc Opening Fund Requisition Line'

    @api.depends('price_unit', 'product_qty')
    def _compute_sub_total(self):
        for line in self:
            line.sub_total = line.price_unit * line.product_qty

    sequence = fields.Integer(string='Sequence', default=10)
    lc_requisition_id = fields.Many2one('lc.opening.fund.requisition', string="LC Requisition")
    product_id = fields.Many2one('product.product', 'Item Name', track_visibility='onchange', required=True)
    description = fields.Char('Item Code', size=256, track_visibility='onchange')
    hs_code = fields.Char('HS Code', size=256, track_visibility='onchange')
    product_qty = fields.Float('Quantity', track_visibility='onchange', default=1.0)
    price_unit = fields.Float(string='Unit Price', help='Price Unit')
    sub_total = fields.Float(string='Subtotal', help='Subtotal', compute='_compute_sub_total', store=True)
    currency_id = fields.Many2one('res.currency', 'Foreign Currency')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.standard_price or 0.0
            self.hs_code = self.product_id.hs_code
            self.description = self.product_id.display_name

