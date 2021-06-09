# -*- coding: utf-8 -*-
from odoo import api, fields, models, _



class LicenseRenewal(models.Model):
    
    _name = 'vehicle.liecense.renew'
    
  
    
    
    def confirm_renew(self):
        self.state = 'done'
    
    
#    name = fields.Integer(string='ID', required=True, copy=False, readonly=True,
#                       index=True, default=lambda self: _('New'))
    date_from = fields.Date('From Date')
    date_to = fields.Date ("To Date")
    cost = fields.Float('Cost')
    speed_money = fields.Float('Speed Money')
    total_cost = fields.Float('Total Cost', compute='_compute_total_cost')
    state = fields.Selection([('draft', 'Draft'),('done', 'Done')], readonly=True, copy=False, index=True, default='draft')
    licence_id = fields.Many2one('fleet.vehicle.log.contract', string="License ID")
    
    @api.depends('cost', 'speed_money')
    
    def _compute_total_cost(self):
        self.total_cost = self.cost + self.speed_money
    
 
 
class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'
    
    def open_license_renewals(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Licence Renewals',
            'view_mode': 'tree,form',
            'res_model': 'vehicle.liecense.renew',
            'domain': [('licence_id', '=', self.id)],
            
        }
        
    
    def get_renew_count(self):
        count = self.env['vehicle.liecense.renew'].search_count([('licence_id', '=', self.id)])
        self.renew_count = count
        
        
    renew_count = fields.Integer(string='Fuel Logs', compute='get_renew_count')        
    