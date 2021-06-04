# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError

class VehicleDistribution(models.Model):
    _name = 'vehicle.distribution'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vehicle Distribution"

    @api.onchange('own_vehicle_id')
    def on_change_vehicle_id(self):
        for i in self:
            if i.own_vehicle_id:
                i.own_vehicle_driver_id = i.own_vehicle_id.driver_id.id
                i.own_vehicle_driver_contact = i.own_vehicle_id.driver_id.mobile

    def send_for_approval(self):
        self.state = 'approval'

    def approve_vehicle(self):
        self.state = 'approved'
        if self.transport_type == 'own':
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
            self.env['vehicle.history'].create(
                {'user_id': user.id, 'date': fields.date.today(), 'vehicle_id': self.own_vehicle_id.id,
                 'driver_id': self.own_vehicle_driver_id.id})

    def changed_vehicle_status(self):
        if self.transport_type =='own' and self.own_vehicle_id:
            if self.own_vehicle_id.kanban_state == 'blocked':
                self.own_vehicle_id.kanban_state = 'done'
            else:
                raise ValidationError(('Vehicle Already in Used State'))


    def reject_vehicle(self):
        self.state = 'draft'
    name = fields.Char(string='Distribution ID', copy= False, readonly= True)
    transport_type = fields.Selection([('own', 'Own'), ('rent', '3rd Party/Rent')], string="Vehicle Type",
                                      default='own')
    picking_id = fields.Many2one('stock.picking', string="Picking ID")
    own_vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle Number", tracking= True, domain=lambda self: [('state_id', '=', self.env.ref('fleet.fleet_vehicle_state_new_request').id),('kanban_state','=','blocked')],)
    own_vehicle_driver_id = fields.Many2one('res.partner', string='Driver Name', tracking= True)
    own_vehicle_driver_contact = fields.Char('Driver Contact Number')
    rent_vehicle_nbr = fields.Char('Vehicle Number', tracking= True)
    rent_vehicle_driver = fields.Char('Driver Name', tracking= True)
    rent_vehicle_driver_contact = fields.Char('Driver Number')
    remarks = fields.Text('Remarks')
    cost = fields.Float('Estimated Cost', tracking= True)
    state = fields.Selection([('draft', 'Draft'), ('approval', 'Sent for Approval'),('approved', 'Approved')], readonly=True, copy=False, index=True,
                             default='draft')

    @api.model
    def create(self, values):
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('vehicle.distribution')
        return super(VehicleDistribution, self).create(values)
