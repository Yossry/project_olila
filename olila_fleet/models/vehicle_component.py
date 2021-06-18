# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class FleetVehicleTyre(models.Model):
    _name = 'vehicle.components'
    
    name = fields.Char('Name')
    number = fields.Char('Number')
    purchase_date = fields.Date('Purchase Date')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")

    def unlink(self):
        for comp in self:
            raise UserError(_('You can not delete a component.'))
        return super(FleetVehicleTyre, self).unlink()
    

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    doc = fields.Binary('Bill upload')
    file_name = fields.Char("File Name")