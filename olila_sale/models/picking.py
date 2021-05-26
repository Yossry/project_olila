# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Picking(models.Model):
    _inherit = 'stock.picking'

    fleet_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    transport_type = fields.Selection([('normal', 'Normal'), ('other', 'Other')])
    transporter_name = fields.Char()
    vehicle_no = fields.Integer()
    driver_name = fields.Char()
    driver_mobile = fields.Integer()
    contact_no = fields.Integer()
