# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class FleetVehicleTyre(models.Model):
    _name = 'vehicle.components'
    
    name = fields.Char('Name')
    number = fields.Char('Number')
    purchase_date = fields.Date('Purchase Date')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
  

class FleetVehicleTyre(models.Model):
    _name = 'vehicle.tyre.detail'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('tyre_no_unique',
         'unique(tyre_no)',
         'Tyre No Has to be Unique!')
      ]
    
    name = fields.Char(string='Name', copy=False, readonly=True)
    tyre_no = fields.Char(string='Tyre No',tracking= True)
    purchase_date = fields.Date('Purchase Date')
    position = fields.Selection([('fl', 'Front-Left'),('fr', 'Front-Right'),('bl', 'Back-Left'),('br', 'Back-Right'),
                                 ('ml', 'Middle-Left'),('mr', 'Middle-Right')
                                 
                                 ], string="Position")
    
    vehicle_id = fields.Many2one('fleet.vehicle', string="vehicle")
    tyre_ids = fields.One2many('vehicle.tyre.retreading' , 'tyre_id', string="Rethreading")
    state = fields.Selection([('open', 'Open'),('lock', 'Lock')], string="State", default='open',tracking= True)
    current_user_id = fields.Many2one('res.users', 'Created By', default=lambda self: self.env.user, store=True,tracking= True)
    

    @api.model
    def create(self, values):
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('vehicle.tyre.detail')
        return super(FleetVehicleTyre, self).create(values)

    def action_lock(self):
        self.state = 'lock'




class TyreRetreading(models.Model):   
    _name = 'vehicle.tyre.retreading'
    
    tyre_id = fields.Many2one('vehicle.tyre.detail', string="Rethreading")
    retreading = fields.Selection([('y', 'Yes'),('n', 'No')
                                 ], string="Retreading")
    date = fields.Date('Date')
    cost = fields.Float('Cost')
    doc = fields.Binary('Bill upload')
    file_name = fields.Char("File Name")
    
       
