# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_color(self):
        for rec in self:
            if rec.picking_type_code == 'outgoing':
                rec.color =  1
            else:
                rec.color = 7


    color = fields.Integer(string='Color Index',compute='_get_color')

class VehicleDistribution(models.Model):
    _name = 'vehicle.distribution'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vehicle Distribution"

    @api.onchange('transport_type')
    def on_change_transport(self):
        self.rent_vehicle_nbr = ''
        self.vehicle_id = False
        self.driver_id = False
        self.driver_contact = ''
        if self.transport_type == 'own':
            return {'domain': {'driver_id': [('is_driver', '=', True),('nature_driver','=','driver')]}}
        else:
            return {'domain': {'driver_id': [('is_driver', '=', True),('parent_id','=',self.transport_company.id)]}}

            

    @api.onchange('vehicle_id', 'driver_id')
    def on_change_vehicle_id(self):
        for i in self:
            if i.vehicle_id:
                i.driver_id = i.vehicle_id.driver_id.id
                i.driver_contact = i.vehicle_id.driver_id.mobile
            else:
                i.driver_contact = i.driver_id.mobile

    @api.onchange('delivery_ids')
    def on_change_delivery_ids(self):
        filb_values = [(5,0,0)]
        if self.delivery_ids:
            for delivery in self.delivery_ids:
                for line in delivery.move_ids_without_package:
                    prod = (0, 0, {'product_id': line.product_id.id, 
                                  'product_qty': line.product_uom_qty,
                                  'partner_id' : delivery.partner_id.id, 
                                  'picking_id': delivery.id
                        })
                    filb_values.append(prod)
        self.update({
              'product_line_ids': filb_values,
            })


    def send_for_approval(self):
        self.state = 'approval'

    def approve_vehicle(self):
        self.state = 'approved'
        if self.transport_type == 'own':
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
            vehicle_found = self.env['vehicle.history'].search([('vehicle_id', '=', self.vehicle_id.id),('driver_id','=' ,self.driver_id.id),
                                                                ('date', '=', self.date)])
            if vehicle_found:
                for line in self.product_line_ids:
                    updated_data = {
                        'product_line_ids': [(0, 0, {'product_id': line.product_id.id, 'product_qty': line.product_qty,
                                   'picking_id' : line.picking_id.id,'partner_id': line.partner_id.id, 'is_done': True})]}
                    vehicle_found.write(updated_data)
            else:
                history = self.env['vehicle.history'].create(
                {'user_id': user.id, 'date': fields.date.today(), 'vehicle_id': self.vehicle_id.id,
                 'driver_id': self.driver_id.id})
                for line in self.product_line_ids:
                    updated_data = {
                        'product_line_ids': [(0, 0, {'product_id': line.product_id.id, 'product_qty': line.product_qty,
                                   'picking_id' : line.picking_id.id,'partner_id': line.partner_id.id, 'is_done': True})]}
                    history.write(updated_data)

            bill= self.env['account.move']
            journal_id = self.env['account.journal'].search([('name', '=','Vendor Bills')], limit=1)
            bill_data = {
                'type': 'in_invoice',
                'ref': self.name,
                'partner_id': self.driver_id.id,
                'invoice_date': self.date,
                'journal_id': journal_id,
            }
            bill_id = bill.create(bill_data)
            if self.product_id.property_account_expense_id:
                account = self.product_id.property_account_expense_id
            else:
                account = self.product_id.categ_id.property_account_expense_categ_id
            bill_id.write({
                'invoice_line_ids': [(0, 0, {
                    'move_id': bill_id.id,
                    'product_id': self.product_id.id,
                    'quantity': 1.0,
                    'price_unit': self.cost,
                    'account_id': account.id
                 })]
            })


    def changed_vehicle_status(self):
        if self.transport_type =='own' and self.vehicle_id:
            if self.vehicle_id.kanban_state == 'blocked':
                self.vehicle_id.kanban_state = 'done'
            else:
                raise ValidationError(('Vehicle Already in Used State'))
    def genarate_product_line(self):
        for delivery in self.delivery_ids:
            for line in delivery.move_ids_without_package:
                updated_data = {'product_line_ids': [(0, 0, {'product_id': line.product_id.id, 'product_qty': line.product_uom_qty,
                                                             'partner_id' : delivery.partner_id.id, 'picking_id': delivery.id})] }
                self.write(updated_data)

    def reject_vehicle(self):
        self.state = 'draft'

    name = fields.Char(string='Distribution ID', copy= False, readonly= True)
    transport_type = fields.Selection([('own', 'Own'), ('rent', '3rd Party/Rent')], string="Vehicle Type",
                                      default='own')
    # picking_id = fields.Many2one('stock.picking', string="Picking ID")
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle Number", tracking= True, domain=lambda self: [('state_id', '=', self.env.ref('fleet.fleet_vehicle_state_new_request').id),('kanban_state','=','blocked')],)
    driver_id = fields.Many2one('res.partner', string='Driver Name', tracking= True)
    driver_contact = fields.Char('Driver Contact Number')
    transport_company = fields.Many2one('res.partner', string='Transport Company', domain="[('nature_driver','=','third')]")
    rent_vehicle_nbr = fields.Char('Vehicle Number', tracking= True)
    remarks = fields.Text('Remarks')
    date = fields.Date('Date', default=datetime.today())
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    cost = fields.Monetary('Estimated Cost', tracking= True)
    state = fields.Selection([('draft', 'Draft'), ('approval', 'Sent for Approval'),('approved', 'Approved')], readonly=True, copy=False, index=True,
                             default='draft')
    product_line_ids = fields.One2many('distribution.product.line', 'distribution_id', string='Product Lines')
    delivery_ids = fields.Many2many('stock.picking', domain= "[('picking_type_code','in',('outgoing','internal')), ('state','not in',('done','cancel'))]" , string="Pickings")
    product_id = fields.Many2one('product.product', string="Product")
    

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
    picking_id = fields.Many2one('stock.picking', string="Picking ID")
