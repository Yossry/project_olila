# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_is_zero

class Picking(models.Model):
    _inherit = 'stock.picking'

    vehicle_type =  fields.Selection([('on chassis', 'On Chassis'), ('covered van', 'Covered Van')],string="Vehicle Type")
    carton_type = fields.Selection([('inner', 'Inner'), ('master', 'Master')],string="Carton Type")
    capture_barcode = fields.Char(string="Capture Barcode")
    job_number = fields.Char(string="Job/Article Number")
    requestion_number =fields.Char(string="Requestion Number")


class Partner(models.Model):
    _inherit = 'res.partner'

    insurance_vendor = fields.Boolean()

class ProductTemplate(models.Model):
    _inherit = "product.template"

    material_type = fields.Selection([('other_raw_material', 'Other Raw Material'), ('sodium_nitrate', 'Sodium Nitrate')], default='other_raw_material')

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    hs_code = fields.Char('HS Code')
    packing_details = fields.Text()

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id:
            self.hs_code = self.product_id.hs_code
        return res

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity', 'qty_received', 'product_uom_qty', 'order_id.state')
    def _compute_qty_invoiced(self):
        for line in self:
            # compute qty_invoiced
            qty = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.move_id.state not in ['cancel']:
                    if inv_line.move_id.move_type == 'in_invoice':
                        qty += inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom)
                    elif inv_line.move_id.move_type == 'in_refund':
                        qty -= inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom)
            line.qty_invoiced = qty

            # compute qty_to_invoice
            if line.order_id.state in ['purchase', 'done', 'landed_cost']:
                if line.product_id.purchase_method == 'purchase':
                    line.qty_to_invoice = line.product_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_received - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

class Purchase(models.Model):
    _inherit = 'purchase.order'

    country_id = fields.Many2one('res.country', string='Country')
    beneficiary = fields.Many2one('res.partner')
    beneficiary_address = fields.Char(string="Beneficiary address")
    beneficiary_bank_name = fields.Char(string="Beneficiary Bank Name")
    beneficiary_bank_branch = fields.Char(string="Beneficiary Bank Branch")
    beneficiary_bank_account_no = fields.Char(string="Beneficiary Account No")
    swift_code  = fields.Char(string="Swift Code")
    # transport
    date_of_last_shipment =  fields.Date()
    pi_date =  fields.Date(string='PI Date')
    port_of_loading  = fields.Char()
    transportation_time = fields.Char()
    transhipment = fields.Char(string="Transhipment", copy=False)
    partial_shipment = fields.Char(string="Partial Shipment", copy=False)
    port_of_landing  = fields.Char(string="Port of Landing", copy=False)
    # others
    purchase_type = fields.Selection([('local', 'Local'), ('import', 'Import')], copy=False)
    state = fields.Selection(selection_add=[('landed_cost', 'LC Opening')], ondelete={'landed': 'set default'})
    landed_cost_count = fields.Integer(compute='_landed_cost_count', string='# Landed Cost')
    mode_of_shipment = fields.Selection([('air', 'Air'), ('ship', 'Ship'), ('road', 'Road')], copy=False)
    

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = super(Purchase, self).onchange_partner_id()
        if self.partner_id:
            self.purchase_type = self.partner_id.olila_seller_type
            self.beneficiary = self.partner_id and self.partner_id.id
        return res

    @api.depends('state', 'order_line.qty_to_invoice')
    def _get_invoiced(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            if order.state not in ('purchase', 'done' , 'landed_cost'):
                order.invoice_status = 'no'
                continue

            if any(
                not float_is_zero(line.qty_to_invoice, precision_digits=precision)
                for line in order.order_line.filtered(lambda l: not l.display_type)
            ):
                order.invoice_status = 'to invoice'
            elif (
                all(
                    float_is_zero(line.qty_to_invoice, precision_digits=precision)
                    for line in order.order_line.filtered(lambda l: not l.display_type)
                )
                and order.invoice_ids
            ):
                order.invoice_status = 'invoiced'
            else:
                order.invoice_status = 'no'

    def unlink(self):
        for line in self:
            if line.state in ['purchase', 'done', 'landed_cost']:
                raise UserError(_('Cannot delete a purchase order line which is in state \'%s\'.') % (line.state,))
        return super(PurchaseOrderLine, self).unlink()

    def button_approve(self, force=False):
        rec = super(Purchase, self).button_approve()
        if self.env.context.get('is_lc'):
            self.write({'state': 'landed_cost', 'date_approve': fields.Datetime.now()})
        return rec

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'landed_cost']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.company.currency_id._convert(
                            order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                if self.purchase_type == 'import':
                    order.write({'state': 'purchase'})
                else:
                    order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

    def _landed_cost_count(self):
        for rec in self:
            requisition_ids = self.env['lc.opening.fund.requisition'].search([('purchase_id', '=', rec.id)])
            rec.landed_cost_count = len(requisition_ids.ids)

    def open_landed_cost(self):
        requisition_ids = self.env['lc.opening.fund.requisition'].search([('purchase_id', '=', self.id)])
        return {
            'name': _('LC Fund Requisition'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'lc.opening.fund.requisition',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', requisition_ids.ids)],
        }

    def _prepare_lines(self, line):
        return {
            'product_id' : line.product_id.id,
            'description' : line.name,
            'hs_code' : line.product_id.hs_code,
            'product_qty' : line.product_qty,
            'price_unit' : line.price_unit,
            'currency_id': line.currency_id and line.currency_id.id
        }

    def _prepare_values(self):
        lines = [(0,0, self._prepare_lines(line)) for line in self.order_line]
        return {
            'supplier_id' : self.partner_id.id,
            'purchase_order_date' : self.create_date,
            'lc_requisition_date' : fields.Date.today(),
            'department_id' : self.department_id and self.department_id.id,
            'purchase_id' : self.id,
            'origin': self.country_id and self.country_id.id,
            'currency_id': self.currency_id and self.currency_id.id,
            'pi_number' : self.partner_ref,
            'pi_date' : self.pi_date,
            'requisition_line_ids' : lines
        }

    def create_landed_cost(self):
        values = self._prepare_values()
        self.env['lc.opening.fund.requisition'].create(values)
        self.write({'state' : 'landed_cost'})
        return True


