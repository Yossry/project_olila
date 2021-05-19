# -*- coding: utf-8 -*-

from odoo import models,fields,api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError, UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class PurchaseRequest(models.Model):

    _name = "purchase.request"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Purchase Request'

    name = fields.Char(default=_('New'), readonly=True, copy=False)
    department_id = fields.Many2one('hr.department', string='Department', required=True)
    schedule_date = fields.Datetime(default=fields.Datetime.now, string='Date')
    team_id = fields.Many2one('committee.committee', string="Committee")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('confirm', 'Confirm'),
        ('waiting', 'Waiting'),
        ('ready', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancel')], default='draft', copy=False, string="State")
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    warehouse_id = fields.Many2one('stock.warehouse', 'Store', ondelete='cascade',
        default=lambda self: self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1))
    amount_total = fields.Float('Total', compute='_compute_amount_total')
    request_lines_ids = fields.One2many('purchase.request.line', 'request_id', 'Request Lines')
    note = fields.Text('Terms and conditions')
    group_id = fields.Many2one('procurement.group', string="Procurement Group", copy=False)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)
    availability = fields.Selection([
        ('not_available', 'Not available'),
        ('available', 'Available in store'),
        ('partial', 'Partially available in store')],
        copy=False, string="Availability", compute='_compute_availability')
    purchase_type = fields.Selection([
        ('gem', 'Gem Portal'),
        ('committee', 'Through Committee'),
        ('local', 'Local Vendor'),
        ('tender', 'Tender Process')], string="Type of Purchase", copy=False)
    picking_count = fields.Integer(compute='_compute_picking', string='Picking count', default=0, store=True)
    tender_count = fields.Integer(default=0)
    picking_ids = fields.Many2many('stock.picking', compute='_compute_picking', string='Pickings', copy=False, store=True)
    show_check_availability = fields.Boolean(compute='_compute_show_check_availability')
    show_tender = fields.Boolean(compute='_compute_tender')
    show_transfer = fields.Boolean(compute='_compute_show_transfer')
    director_approval = fields.Boolean()

    @api.depends('request_lines_ids')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.request_lines_ids.mapped('price_subtotal'))

    def _compute_availability(self):
        if all([line.available_qty == (line.quantity+line.extra_qty) for line in self.request_lines_ids]):
            self.availability = 'available'
        elif any([line.available_qty == (line.quantity+line.extra_qty) for line in self.request_lines_ids]):
            self.availability = 'partial'
        else:
            self.availability = 'not_available'

    def button_approve_direct(self):
        self.write({'state': 'approve', 'director_approval': True})

    @api.depends('request_lines_ids.price_subtotal')
    def _price_total(self):
        self.amount_total = sum(line.price_subtotal for line in self.request_lines_ids)

    def _compute_show_check_availability(self):
        show_check_availability = False
        for picking in self.picking_ids:
            has_moves_to_reserve = any(
                move.state in ('waiting', 'confirmed', 'partially_available') and
                float_compare(move.product_uom_qty, 0, precision_rounding=move.product_uom.rounding)
                for move in picking.move_lines
            )
            picking.show_check_availability = picking.is_locked and picking.state in ('confirmed', 'waiting', 'assigned') and has_moves_to_reserve
            if picking.show_check_availability:
                show_check_availability = True
        self.show_check_availability = show_check_availability

    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]
        result['context'] = {}
        pick_ids = self.mapped('picking_ids')
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids.id
        return result

    def action_view_tender(self):
        action = self.env.ref('purchase_requisition.action_purchase_requisition')
        result = action.read()[0]
        result['context'] = {}
        tender_ids = self.request_lines_ids.mapped('tender_id')
        if not tender_ids or len(tender_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (tender_ids.ids)
        elif len(tender_ids) == 1:
            res = self.env.ref('purchase_requisition.view_purchase_requisition_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = tender_ids.id
        return result

    @api.depends('request_lines_ids.move_ids.returned_move_ids',
                 'request_lines_ids.move_ids.state',
                 'request_lines_ids.move_ids.picking_id')
    def _compute_picking(self):
        for request in self:
            pickings = self.env['stock.picking']
            for line in request.request_lines_ids:
                moves = line.move_ids | line.move_ids.mapped('returned_move_ids')
                pickings |= moves.mapped('picking_id')
            request.picking_ids = pickings
            request.picking_count = len(pickings)

    def _compute_show_transfer(self):
        for request in self:
            if request.state == 'confirm' and request.availability != 'available' and request.picking_count == 0:
                request.show_transfer = True
            request.show_transfer = False

    def _compute_tender(self):
        for request in self:
            request.tender_count = len(request.request_lines_ids.mapped('tender_id').filtered(lambda x: x.state != 'cancel'))
            if request.tender_count == 0 and request.state in ('confirm', 'waiting') and request.availability != 'available':
                request.show_tender = True
            request.show_tender = False

    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('purchase.request')
        return super(PurchaseRequest, self).create(values)

    def unlink(self):
        for request in self:
            if request.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete an request which is not draft or cancelled.'))
        return super(PurchaseRequest, self).unlink()

    def button_tender(self):
        lines = []
        # if not self.purchase_type:
        #     raise UserError(_('Please select purchase type.'))
        for line in self.request_lines_ids.filtered(lambda x:(x.quantity + x.extra_qty) > x.available_qty):
            remaining_qty = abs((line.quantity + line.extra_qty) - line.available_qty)
            if remaining_qty:
                tendor_vals = {
                    'origin': self.name,
                    'date_end': self.schedule_date,
                    'warehouse_id': self.warehouse_id.id,
                    'company_id': self.company_id.id,
                    'picking_type_id': self.department_id.picking_type.id,
                    'purchase_request_id': self.id,
                    'line_ids': [(0, 0, {
                                    'product_id': line.product_id.id,
                                    'product_uom_id': line.product_uom.id,
                                    'product_qty': remaining_qty,
                                    'price_unit': line.price_unit if line.request_id.purchase_type == 'gem' else 0.0,
                                    'scheduled_date': line.date if line.request_id.purchase_type == 'gem' else False,
                                    'move_dest_id': line.move_ids.mapped('move_dest_ids') and line.move_ids.mapped('move_dest_ids')[0].id or False,
                                })],
                }
                tender_id = self.env['purchase.requisition'].create(tendor_vals)
                line.write({'tender_id': tender_id.id})

    def button_transfer(self):
        if not self.department_id.location_id:
            raise ValidationError(_('Please set location on department.'))
        if not self.department_id.picking_type:
            raise ValidationError(_('Please set picking type on department.'))
        if len(self.request_lines_ids) == 0:
            raise ValidationError(_('Please add at least one request line'))
        vals = self._prepare_stock_move_vals()
        for data in vals:
            self.env['stock.move'].create(data)
        if self.request_lines_ids.mapped('move_ids').filtered(lambda x: x.state not in ('done')):
            self.request_lines_ids.mapped('move_ids')._action_confirm()
        self.button_done()

    def button_approval(self):
        self.write({'state': 'approve'})

    def button_confirm(self):
        if self.amount_total > 25000 and not self.director_approval:
            raise ValidationError(_('You needs approval of director becuase amount is more then 25000'))
        self.write({'state': 'confirm'})

    def button_draft(self):
        self.write({'state': 'draft', 'director_approval': False})

    def check_availability(self):
        import pdb
        pdb.set_trace()
        self.request_lines_ids.mapped('move_ids')._action_assign()
        state = 'waiting'
        for line in self.request_lines_ids:
            quant_ids = line.product_id.stock_quant_ids.filtered(lambda x:x.location_id.usage == 'internal')
            onhand_qty =  sum(quant_ids.mapped('quantity')) - sum(quant_ids.mapped('reserved_quantity'))
            line_qty = line.quantity + line.extra_qty
            if onhand_qty >= line_qty or line.product_id.type != 'product':
                line.available_qty = line_qty
            else:
                line.available_qty = onhand_qty
        if all(rec.quantity+rec.extra_qty == rec.available_qty for rec in self.request_lines_ids):
            state = 'ready'
        self.write({'state': state})

    def button_cancel(self):
        self.picking_ids.action_cancel()
        tenders = self.request_lines_ids.mapped('tender_id')
        if tenders:
            tenders.action_cancel()
        self.request_lines_ids.write({'available_qty': 0})
        self.write({'state': 'cancel'})

    def button_done(self):
        self.write({'state': 'done'})

    def _prepare_stock_move_vals(self):
        vals = []
        warehouse_id = self.warehouse_id
        location_id = warehouse_id.lot_stock_id
        location_dest_id = self.department_id.location_id
        picking_type = self.department_id.picking_type
        if not self.group_id:
            self.group_id = self.group_id.create({'name': self.name})
        for line in self.request_lines_ids:
            vals.append({
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product_uom.id,
                'picking_type_id': picking_type.id,
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
                'group_id': self.group_id.id if self.group_id else False,
                'company_id': self.company_id.id,
                'warehouse_id': warehouse_id.id,
                'request_line_id': line.id,
                'origin': self.name,
            })
        return vals


class PurchaseRequestLine(models.Model):

    _name = "purchase.request.line"
    _description = "request.line"

    request_id = fields.Many2one('purchase.request')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Text(string='Description', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    available_qty = fields.Float(string='Reserved Qty', readonly=True, default=0)
    price_unit = fields.Float('Unit Price', required=True, default=0.0)
    product_uom = fields.Many2one('uom.uom', string='UOM')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price')
    move_ids = fields.One2many('stock.move', 'request_line_id')
    is_done = fields.Boolean('Done', compute='_compute_is_done', store=True)
    tender_id = fields.Many2one('purchase.requisition', 'Tender')
    extra_qty = fields.Float('Extra Qty')
    date = fields.Datetime('Date')

    availability = fields.Selection(related='request_id.availability')


    @api.depends('price_unit','quantity','product_id', 'extra_qty')
    def _compute_price(self):
        for rec in self:
            rec.price_subtotal = (rec.extra_qty + rec.quantity) * rec.price_unit

    @api.depends('request_id.state')
    def _compute_is_done(self):
        for line in self:
            line.is_done = (line.request_id.state in ('done', 'cancel'))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.display_name
            self.product_uom = self.product_id.uom_id and self.product_id.uom_id.id or False
