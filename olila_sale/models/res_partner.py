# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

    # is_dealer = fields.Boolean(string="Is Dealer")
    # is_distributors = fields.Boolean(string="Is Distributors")
    blila_code = fields.Char('Code', index=True, copy=False, default="New")
    deport_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    vertule_warehouse_id = fields.Many2one('stock.warehouse', string='Vertule Warehouse Distributor')
    olila_type = fields.Selection(selection=[('dealer', 'Dealer'), ('distributor', 'Distributor')], string="Olala Type")
    status = fields.Selection(selection=[('active', 'Active'), ('dormant', 'Dormant')], string="Status")
    blila_pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True)
    national_identifi_number = fields.Char(string="National Identifi Number", colpy="False")
    blila_document = fields.Binary('Upload Documents' , attachment=False)

    @api.model
    def create(self, vals):
        res = super(Partner, self).create(vals)
        if res.olila_type == 'dealer':
            res.blila_code = self.env['ir.sequence'].next_by_code('res.partner') or '/'
        return res