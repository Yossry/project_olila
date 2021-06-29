# -*- coding: utf-8 -*-
from odoo import api, fields, models, _



class LicenseRenewal(models.Model):
    _rec_name = 'date_from'
    _name = 'vehicle.liecense.renew'
    
  
    
    
    def confirm_renew(self):
        self.state = 'done'
    
    
#    name = fields.Integer(string='ID', required=True, copy=False, readonly=True,
#                       index=True, default=lambda self: _('New'))
    date_from = fields.Date('From Date')
    date_to = fields.Date ("To Date")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    cost = fields.Monetary('Cost')
    speed_money = fields.Monetary('Speed Money')
    total_cost = fields.Monetary('Total Cost', compute='_compute_total_cost', store=True)
    state = fields.Selection([('draft', 'Draft'),('done', 'Done')], readonly=True, copy=False, default='draft')
    licence_id = fields.Many2one('fleet.vehicle.log.contract', string="License ID")
    doc1 = fields.Binary('Licence Renewal')
    file_name = fields.Char("Licence Renewal")


    @api.depends('cost', 'speed_money')    
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.cost + rec.speed_money
    
 
 
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
    