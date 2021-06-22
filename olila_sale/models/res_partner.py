# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

    def _get_type(self):
        res = [('corporater', 'Corporate'), ('dealer', 'Dealer'), ('distributor', 'Distributor')]
        return res

    def _get_seller_type(self):
        res = [('local', 'Local'), ('import', 'Import')]
        return res

    code = fields.Char('Code', index=True, copy=False, default="New")
    deport_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', copy=False)
    vertual_location_id = fields.Many2one('stock.location', string='Virtual Location For Distributor')
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