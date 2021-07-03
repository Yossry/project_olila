# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Picking(models.Model):
    _inherit = 'stock.picking'

    fleet_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    transport_type = fields.Selection([('normal', 'Normal'), ('other', 'Other')])
    transporter_name = fields.Char(string="Transpoter Type")
    vehicle_no = fields.Integer(string="Vehicle No")
    driver_name = fields.Char(string="Driver Name")
    driver_mobile = fields.Integer(string="Driver Mobile No")
    contact_no = fields.Integer()
    requestion_number = fields.Char(string="Requisition Number")
    carton_type = fields.Selection([('normal', 'Normal'), ('other', 'Other')], string="Carton Type")
    capture_barcode = fields.Char(string="Capture Barcode")
    job_article_number = fields.Char(string="Job Article Number")
    