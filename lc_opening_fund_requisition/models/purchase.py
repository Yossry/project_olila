# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = "product.template"

    material_type = fields.Selection([('other_raw_material', 'Other Raw Material'), ('sodium_nitrate', 'Sodium Nitrate')], default='other_raw_material')

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    hs_code = fields.Char('HS Code', size=256)

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id:
            self.hs_code = self.product_id.hs_code
        return res

class Purchase(models.Model):
    _inherit = 'purchase.order'

    # buyer
    buyer_name = fields.Many2one('res.partner', string="Buyer")
    origin = fields.Many2one('res.country')
    buyer_address = fields.Char()
    buyer_factory_address = fields.Char()
    # account
    beneficiary = fields.Char()
    beneficiary_address = fields.Char()
    beneficiary_bank_name = fields.Char()
    beneficiary_bank_branch = fields.Char()
    beneficiary_bank_account_no = fields.Char()
    swift_code  = fields.Char()
    # transport
    packing_details = fields.Text()
    date_of_last_shipment =  fields.Date()
    port_of_loading  = fields.Char()
    transportation_time = fields.Char()
    transhipment = fields.Char()
    # others
    purchase_type = fields.Selection([('local', 'Local'), ('import', 'Import')], default='local', copy=False)
    state = fields.Selection(selection_add=[('landed_cost', 'LC Opening')], ondelete={'landed': 'set default'})
    landed_cost_count = fields.Integer(compute='_landed_cost_count', string='# Landed Cost')
    mode_of_shipment = fields.Selection([('air', 'Air'), ('ship', 'Ship'), ('road', 'Road')], copy=False) 

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.company.currency_id._convert(
                            order.company_id.po_double_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                if self.purchase_type != 'import':
                    order.button_approve()
                else:
                    self.write({'state': 'purchase'})

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
            'name': _('Landed Costs'),
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
            'price_unit' : line.price_unit
        }

    def _prepare_values(self):
        lines = [(0,0, self._prepare_lines(line)) for line in self.order_line]
        return {
            'supplier_id' : self.partner_id.id,
            'purchase_orde_date' : self.create_date,
            'lc_requisition_date' : fields.Date.today(),
            'purchase_id' : self.id,
            'requisition_line_ids' : lines
        }

    def create_landed_cost(self):
        values = self._prepare_values()
        self.env['lc.opening.fund.requisition'].create(values)
        self.write({'state' : 'landed_cost'})
        return True


