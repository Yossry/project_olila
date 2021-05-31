
from odoo import api, fields, models


class FleetVehicle(models.Model):
    
    _inherit = 'fleet.vehicle'
    
    txt_field = fields.Text("New Text Field")
    registration_nbr = fields.Text('Vehicle Registration No')
    date_purchase = fields.Date('Vehicle Purchase Date')
    cubic_centimeter = fields.Text("Vehicle Cubic Capacity (CC)")
    vehicle_status = fields.Selection([('u', 'Use'),('i', 'Idle')], string="Vehicle Status")
    vehicle_actuve_status = fields.Selection([('a', 'Active'),('r', 'Repairing'),('b', 'Breakdown'),('s', 'Scrap')], string="Vehicle Active Status")
    vehicle_type = fields.Many2many('fleet.vehicle.tag', string="Vehicle Type")
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
    fuel_log_count = fields.Integer(string='Fuel Logs', compute='get_fuel_log_count')
    average_milage = fields.Char('Average Mileage')
    vehicle_seat = fields.Float('Seat/Capacity')
    components_ids = fields.One2many('vehicle.components', 'vehicle_id', string='Components')
    vehicle_asign = fields.Many2one('hr.employee', string="Vehicle Asigned To")
    # future_driver_mobile = fields.Char(related='future_driver_id.mobile')
    
    
    
    
    
    def open_vehicle_tyres(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tyres',
            'view_mode': 'tree,form',
            'res_model': 'vehicle.tyre.detail',
            'domain': [('vehicle_id', '=', self.id)],
            
        }
        
    

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
            
        }
    
    def get_fuel_log_count(self):
        count = self.env['fleet.vehicle.log.fuel'].search_count([('vehicle_id', '=', self.id)])
        self.fuel_log_count = count
    