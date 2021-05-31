# -*- coding: utf-8 -*-

from odoo import api, fields, models

class FleetVehicleTyre(models.Model):
    _name = 'vehicle.components'
    
    name = fields.Char('Name')
    number = fields.Char('Number')
    purchase_date = fields.Date('Purchase Date')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    
    