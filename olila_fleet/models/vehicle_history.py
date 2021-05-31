# -*- coding: utf-8 -*-
from odoo import api, fields, models,_

class VehicleHistory(models.Model):
    _name = 'vehicle.history'
    _description = "Vehicle History"



    name = fields.Char(string='Distribution ID', copy=False, readonly=True)
    user_id = fields.Many2one('res.users', string='Created By')
    date = fields.Date('Date')
    driver_id = fields.Many2one('res.partner', string='Driver Name')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")



    @api.model
    def create(self, values):
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('vehicle.history')
        return super(VehicleHistory, self).create(values)