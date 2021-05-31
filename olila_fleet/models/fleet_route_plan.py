# -*- coding: utf-8 -*-
from odoo import api, fields, models

class FleetRoutePlan(models.Model):
    _name = 'fleet.route.plan'
    
    def confirm_route(self):
        self.state = 'done'
    
    date = fields.Date('Date')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    components_ids = fields.One2many('fleet.route.plan.line', 'route_id', string='Dealer Names')
    state = fields.Selection([('draft', 'Draft'),('done', 'Done')], readonly=True, copy=False, index=True, default='draft')
 
 
 
 

class FleetRoutePlanLine(models.Model):
    _name = 'fleet.route.plan.line' 
    
    customer = fields.Many2one('res.partner', string="Dealer")
    street =   fields.Char('Street' , related='customer.street')
    street2 =   fields.Char('Street' , related='customer.street2')
    city =   fields.Char('Street' , related='customer.city')
    route_id = fields.Many2one('fleet.route.plan', string="Route_id")