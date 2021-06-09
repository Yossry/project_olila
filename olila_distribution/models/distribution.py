# -*- coding: utf-8 -*-
from datetime import datetime
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
            vehicle_found = self.env['vehicle.history'].search([('vehicle_id', '=', self.own_vehicle_id.id),('driver_id','=' ,self.own_vehicle_driver_id.id),
                                                                ('date', '=', self.date)])
            if vehicle_found:
                for line in self.product_line_ids:
                    updated_data = {
                        'product_line_ids': [(0, 0, {'product_id': line.product_id.id, 'product_qty': line.product_qty,
                                   'picking_id' : self.picking_id.id,'partner_id': line.partner_id.id, 'is_done': True})]}
                    vehicle_found.write(updated_data)
            else:
                history = self.env['vehicle.history'].create(
                {'user_id': user.id, 'date': fields.date.today(), 'vehicle_id': self.own_vehicle_id.id,
                 'driver_id': self.own_vehicle_driver_id.id})
                for line in self.product_line_ids:
                    updated_data = {
                        'product_line_ids': [(0, 0, {'product_id': line.product_id.id, 'product_qty': line.product_qty,
                                   'picking_id' : self.picking_id.id,'partner_id': line.partner_id.id, 'is_done': True})]}
                    history.write(updated_data)

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

    def genarate_product_line(self):
        for rec in self:
            if rec.state == 'done':
                done = True
            else:
                done = False
            for line in self.picking_id.move_line_ids_without_package:
                updated_data = {'product_line_ids': [(0, 0, {'product_id': line.product_id.id, 'product_qty': line.product_uom_qty,
                                                             'partner_id' : rec.picking_id.partner_id.id, 'is_done':done})] }
                rec.write(updated_data)

    picking_id = fields.Many2one('stock.picking', string="Picking ID")
    own_vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle Number", tracking= True, domain=lambda self: [('state_id', '=', self.env.ref('fleet.fleet_vehicle_state_new_request').id),('kanban_state','=','blocked')],)
    own_vehicle_driver_id = fields.Many2one('res.partner', string='Driver Name', tracking= True)
    own_vehicle_driver_contact = fields.Char('Driver Contact Number')
    rent_vehicle_nbr = fields.Char('Vehicle Number', tracking= True)
    rent_vehicle_driver = fields.Char('Driver Name', tracking= True)
    rent_vehicle_driver_contact = fields.Char('Driver Number')
    remarks = fields.Text('Remarks')
    date = fields.Date('Date', default=datetime.today())
    cost = fields.Float('Estimated Cost', tracking= True)
    state = fields.Selection([('draft', 'Draft'), ('approval', 'Sent for Approval'),('approved', 'Approved')], readonly=True, copy=False, index=True,
                             default='draft')
    product_line_ids = fields.One2many('distribution.product.line', 'distribution_id', string='Product Lines')

    @api.model
    def create(self, values):
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('vehicle.distribution')
        return super(VehicleDistribution, self).create(values)


class DistributionProductLine(models.Model):
    _name = 'distribution.product.line'

    distribution_id = fields.Many2one('vehicle.distribution', string='Distribution ID')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float('Quantity')
    partner_id = fields.Many2one('res.partner', 'Delivery Address')
    is_done = fields.Boolean('Done')
