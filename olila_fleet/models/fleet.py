# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from odoo import api, fields, models

class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'
 
    vehicle_type = fields.Selection([('cover_van', 'Covered Van'), ('car', 'Car'), ('bike', 'Motor Bike')], default='car', required=True)
    
    @api.depends('name', 'brand_id', 'vehicle_type')
    def name_get(self):
        ret_list = []
        for record in self:
            name = record.name
            if record.brand_id.name:
                name = record.brand_id.name + '/' + name
                if record.vehicle_type:
                    name = name + '(' + record.vehicle_type + ')'
            ret_list.append((record.id, name))
        return ret_list


class FleetVehicle(models.Model):    
    _inherit = 'fleet.vehicle'

    @api.onchange('driver_id')
    def on_change_driver_id(self):
        for i in self:
            if i.driver_id:
                i.driver_number = i.driver_id.mobile

    @api.onchange('helper_id')
    def on_change_future_driver_id(self):
        for i in self:
            if i.helper_id:
                i.helper_number = i.helper_id.mobile

    @api.onchange('department_id')
    def on_change_department_id(self):

         if self.department_id:
            return {'domain': {'vehicle_asign_id': [('department_id', '=', self.department_id.id)]}}
    
    registration_nbr = fields.Text('Vehicle Registration No')
    date_purchase = fields.Date('Vehicle Purchase Date')
    cubic_centimeter = fields.Float("Vehicle Cubic Capacity (CC)")
    kanban_state = fields.Selection([
        ('done', 'USED'),
        ('blocked', 'IDLE'),
        ], string='Vehicle Status',
        copy=False, default='blocked', tracking=True
    )

    doc1 = fields.Binary('Doc 1')
    file_name = fields.Char("File Name")
    doc2 = fields.Binary('Doc 2')
    file_name2 = fields.Char("File Name")
    doc3 = fields.Binary('Doc 3')
    file_name3 = fields.Char("File Name")
    doc4 = fields.Binary('Doc 4')
    file_name4 = fields.Char("File Name")
    doc5 = fields.Binary('Doc 5')
    file_name5 = fields.Char("File Name")

    tyres_count = fields.Integer(string='Tyres', compute='get_tyres_count')
    fuel_type = fields.Selection([('gasoline', 'Petrol'),('lpg', 'CNG'),('diesel', 'Diesel'),('electric','Electric'),('hybrid','Hybrid')], string="Fuel Type")

    fuel_log_count = fields.Integer(string='Fuel Logs', compute='get_fuel_log_count')
    vehicle_seat = fields.Float('Seat/Capacity')
    # components_ids = fields.One2many('vehicle.components', 'vehicle_id', string='Components')
    vehicle_asign_id = fields.Many2one('hr.employee', string="Vehicle Assigned To")
#added fuel_type and rootes_count    
    routes_count = fields.Integer(string='Tyres', compute='get_routes_count')
    component_count = fields.Integer(string='Component', compute='get_component_count')
    average_mileage = fields.Float(string='Average Mileage')
    driver_number = fields.Char('Driver Number')
    helper_id = fields.Many2one('res.partner', string='Helper Name')
    helper_number = fields.Char('Helper Number')
    department_id = fields.Many2one('hr.department', string='Department')
    driver_nid = fields.Char('Driver ID')
    vehicle_history_count = fields.Integer(string='Fuel Logs', compute='get_vehicle_history_count')



        
    def open_vehicle_tyres(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tyres',
            'view_mode': 'tree,form',
            'res_model': 'vehicle.tyre.detail',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}  
            
        }

    def open_vehicle_component(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Components',
            'view_mode': 'tree,form',
            'res_model': 'vehicle.components',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}  
            
        }

    def get_component_count(self):
        count = self.env['vehicle.components'].search_count([('vehicle_id', '=', self.id)])
        self.component_count = count
        
    
    def get_tyres_count(self):
        count = self.env['vehicle.tyre.detail'].search_count([('vehicle_id', '=', self.id)])
        self.tyres_count = count
    

    def open_vehicle_fuel_logs(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fuel Issue',
            'view_mode': 'tree,form',
            'res_model': 'fleet.vehicle.log.fuel',
            'domain': [('vehicle_id', '=', self.id)], 
            'context': {'default_vehicle_id': self.id}  

        }
    
    def get_fuel_log_count(self):
        count = self.env['fleet.vehicle.log.fuel'].search_count([('vehicle_id', '=', self.id)])
        self.fuel_log_count = count
        
# Smart button for Routes    
    def open_vehicle_routes(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Routes',
            'view_mode': 'tree,form',
            'res_model': 'fleet.route.plan',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}  
            
        }
        
# Routes Count    
    def get_routes_count(self):
        count = self.env['fleet.route.plan'].search_count([('vehicle_id', '=', self.id)])
        self.routes_count = count

    def open_vehicle_history(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle History',
            'view_mode': 'tree,form',
            'res_model': 'vehicle.history',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}

        }

    def get_vehicle_history_count(self):
        count = self.env['vehicle.history'].search_count([('vehicle_id', '=', self.id)])
        self.vehicle_history_count = count
        
# Document Upload in Vehicle Service 
        
class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    
    doc = fields.Binary('Bill Upload')
    file_name = fields.Char("File Name")        

    