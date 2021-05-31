# -*- coding: utf-8 -*-
from odoo import api, fields, models

class FleetVehicleTyre(models.Model):
    _name = 'vehicle.components'
    
    name = fields.Char('Name')
    number = fields.Char('Number')
    purchase_date = fields.Date('Purchase Date')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
  

class FleetVehicleTyre(models.Model):
    _name = 'vehicle.tyre.detail'
    
    name = fields.Char('Tyre No')
    purchase_date = fields.Date('Purchase Date')
    position = fields.Selection([('fl', 'Front-Left'),('fr', 'Front-Right'),('bl', 'Back-Left'),('br', 'Back-Right'),
                                 ('ml', 'Middle-Left'),('mr', 'Middle-Right')
                                 
                                 ], string="Position")
    
    vehicle_id = fields.Many2one('fleet.vehicle', string="vehicle")
    tyre_ids = fields.One2many('vehicle.tyre.retreading' , 'tyre_id', string="Rethreading")
    
    
class TyreRetreading(models.Model):   
    _name = 'vehicle.tyre.retreading'
    
    tyre_id = fields.Many2one('vehicle.tyre.detail', string="Rethreading")
    retreading = fields.Selection([('y', 'Yes'),('n', 'No')
                                 ], string="Retreading")
    date = fields.Date('Date')
    cost = fields.Float('Cost')
    doc = fields.Binary('Bill upload')
    file_name = fields.Char("File Name")
    
       