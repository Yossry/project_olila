# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

    def _get_customer_location(self):
        customer_location, supplier_location = self.env['stock.warehouse']._get_partner_locations()
        return customer_location

    def _get_type(self):
        res = [('corporater', 'Corporate'), ('dealer', 'Dealer'), ('distributor', 'Distributor')]
        return res

    def _get_seller_type(self):
        res = [('local', 'Local'), ('import', 'Import')]
        return res

    code = fields.Char('Code', index=True, copy=False, default="New")
    deport_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', copy=False)
    vertual_location_id = fields.Many2one('stock.location', string='Virtual Location For Distributor', default=_get_customer_location)
    distributor_id = fields.Many2one("res.partner", string="Distributor", copy=False)
    proprietor_name = fields.Char("Proprietor Name")
    proprietor_contact = fields.Char("Proprietor Contact")
    olila_type = fields.Selection(selection=_get_type, string="Customer Type")
    bin_no = fields.Char("BIN No")
    ref_name = fields.Char(string="Ref No")
    tin_no = fields.Char(string="TIN no")
    tin_no_document = fields.Binary('Copy of TIN no', attachment=True)
    olila_seller_type = fields.Selection(selection=_get_seller_type, string="Vendor Type")
    national_identifi_number = fields.Char(string="National Identification Number", copy=False)
    olila_ni_document = fields.Binary('National Identification Documents', attachment=True)
    trade_licence = fields.Char(string="Trade Licence", copy=False)
    trade_licence_document = fields.Binary('Copy of Trade Lince', attachment=True)
    zone_id = fields.Many2one('res.zone', string='Zone', copy=False)
    secondary_contact_persion = fields.Char("Secondary Contact Person")
    responsible = fields.Many2one('hr.employee', string="Responsible")
    is_customer = fields.Boolean(string="Customer", compute="_compute_is_customer", inverse="_set_is_customer", store=True)
    is_supplier = fields.Boolean(string="Supplier", compute="_compute_is_supplier", inverse="_set_is_supplier", store=True)

    @api.model
    def create(self, vals):
        res = super(Partner, self).create(vals)
        res.code = self.env['ir.sequence'].next_by_code('res.partner') or '/'
        return res

    @api.onchange('distributor_id')
    def _onchange_distributor(self):
        if self.distributor_id:
            self.proprietor_name = self.distributor_id.proprietor_name
            self.proprietor_contact = self.distributor_id.proprietor_contact

    @api.onchange('vertual_location_id')
    def _onchange_olila_type(self):
        if self.olila_type == 'distributor' and self.vertual_location_id:
            self.property_stock_customer = self.vertual_location_id.id

    @api.depends('customer_rank')
    def _compute_is_customer(self):
        for rec in self:
            rec.is_customer = bool(rec.customer_rank)

    def _set_is_customer(self):
        self.customer_rank = 1 if self.is_customer else 0

    def _set_is_supplier(self):
        self.supplier_rank = 1 if self.is_supplier else 0

    @api.depends('supplier_rank')
    def _compute_is_supplier(self):
        for rec in self:
            rec.is_supplier = bool(rec.supplier_rank)

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        if name:
            args = args + [('code', operator, name)]
        res = super(Partner, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
        partners = self.search(args)
        if name:
            res = res + partners.ids
        return res
