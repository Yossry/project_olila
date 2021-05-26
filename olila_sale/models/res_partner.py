# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

    def _get_type(self):
        res = [('none', 'Not Customer'), ('dealer', 'Dealer'), ('distributor', 'Distributor')]
        return res

    def _get_seller_type(self):
        res = [('none', 'Not Seller'), ('local', 'Local'), ('import', 'Import')]
        return res

    code = fields.Char('Code', index=True, copy=False, default="New")
    deport_warehouse_id = fields.Many2one('stock.warehouse', string='Olila Warehouse')
    vertual_warehouse_id = fields.Many2one('stock.location', string='virtual Location For Distributor')
    distributor_id = fields.Many2one("res.partner", string="Distributor", copy=False)
    proprietor_name = fields.Char("Proprietor Name")
    proprietor_contact = fields.Char("Proprietor Contact")
    olila_type = fields.Selection(selection=_get_type, string="Olala Type")
    bin_no = fields.Char("BIN No")
    ref_name = fields.Char(string="Ref No")
    olila_seller_type = fields.Selection(selection=_get_seller_type, string="Olala Type")
    national_identifi_number = fields.Char(string="National Identifi Number", copy=False)
    olila_ni_document = fields.Binary('National Identification Documents', attachment=True)
    trade_licence = fields.Char(string="Trade Licence", copy=False)
    trade_licence_document = fields.Binary('Copy of Trade Lince', attachment=True)
    zone = fields.Char("Zone")
    secondary_contact_persion = fields.Char("Secondary Contact Persion")

    @api.model
    def create(self, vals):
        res = super(Partner, self).create(vals)
        if res.olila_type == 'dealer':
            res.code = self.env['ir.sequence'].next_by_code('res.partner') or '/'
        elif res.olila_type == 'distributor':
            res.code = self.env['ir.sequence'].next_by_code('res.partner') or '/'
        return res