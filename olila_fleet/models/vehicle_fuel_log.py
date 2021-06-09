# -*- coding: utf-8 -*-
from odoo import api, fields, models

class FleetVehicleFuelLog(models.Model):    
    _name = 'fleet.vehicle.log.fuel'
    _rec_name = 'date'
    
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    driver_id = fields.Many2one('res.partner', string="Driver")
    date = fields.Date ('Date')
    ini_km_reading = fields.Float('Initial Reading KM')
    end_km_reading = fields.Float('End Reading KM')
    total_km = fields.Float('Total KM' , compute='_compute_total_km')
    expected_fuel_req = fields.Float('Expected Fuel Requisition')
    fuel_amount = fields.Float('Fuel Purchased (Ltr)')
    amount = fields.Float('Amount')
    doc1 = fields.Binary('Bill upload')
    file_name = fields.Char("File Name")
    fuel_purchase_ids = fields.One2many('fuel.purchase.history', 'fuel_log_id', string="Fuel Purchase History")
    state = fields.Selection([('open', 'Open'), ('lock', 'Lock')], string="State", default='open', tracking=True)

    
    
    @api.depends('end_km_reading', 'ini_km_reading')
    def _compute_total_km(self):
        for rec in self:
            rec.total_km = rec.end_km_reading - rec.ini_km_reading

    def action_lock(self):
        self.state = 'lock'


class FleetVehicleFuelLog(models.Model):
    _name = 'fuel.purchase.history'

    fuel_log_id = fields.Many2one('fleet.vehicle.log.fuel', string='Fuel Log')
    fuel_purchase = fields.Float('Fuel Purchase(litre)')
    fuel_type = fields.Selection([('gasoline', 'Petrol'),('lpg', 'CNG'),('diesel', 'Diesel'),('octane','Octane')], string="Fuel Type")
    amount = fields.Float('Amount')
    doc = fields.Binary('Bill upload')
    file_name = fields.Char("File Name")
    purchase_date = fields.Date("Purchase Date")
