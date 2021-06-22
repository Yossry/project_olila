# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round
import requests
import json

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_type = fields.Selection(selection=[('primary_sales', 'Primary Sales'),
        ('secondary_sales', 'Secondary Sales'), ('corporate_sales', 'Corporate Sales')], default="primary_sales", string="Sale Type")
    dealer_code = fields.Char(string="Dealer Code")
    distributor_code = fields.Char(string="Distributor Code")
    estimation_lines = fields.One2many('cost.estimation', 'order_id', string="Estimation Details")
    subject = fields.Text("Subject")
    sl_no = fields.Char("S/L number")
    contact_no = fields.Char("Contact No")
    zone_id = fields.Many2one('res.zone', string='Zone', copy=False)
    secondary_contact_persion = fields.Char("Secondary Contact Person")
    rfq_id = fields.Many2one('request.for.quote', string="RFQ")

    def action_cost_estimation(self):
        """ Cost Estimation Open"""
        action_rec = self.env['ir.model.data'].sudo().xmlid_to_object('olila_sale.cost_estimation_action')
        if action_rec:
            action = action_rec.sudo().read([])[0]
            action["domain"] = [('order_id', '=', self.id)]
            action['context'] = {'default_order_id': self.id}
            return action
        return True

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            if self.sale_type == 'primary_sales':
                self.dealer_code = self.partner_id.code
                if self.partner_id.deport_warehouse_id:
                    self.warehouse_id = self.partner_id.deport_warehouse_id.id
            elif self.sale_type == 'secondary_sales':
                self.distributor_code = self.partner_id.distributor_id.code
            self.contact_no = self.partner_id and self.partner_id.phone or self.partner_id.mobile
            self.zone_id = self.partner_id and self.partner_id.zone_id.id
            self.secondary_contact_persion = self.partner_id and self.partner_id.secondary_contact_persion
        return super(SaleOrder, self).onchange_partner_id()


class SaleorderLine(models.Model):
    _inherit = 'sale.order.line'

    capture_gps_location = fields.Char(string="Capture GPS Location", copy=False)
    latitude = fields.Char(string="latitude", copy=False)
    longitute = fields.Char(string="Longitute", copy=False)

    @api.model
    def create(self, vals):
        ip_address = request.httprequest.environ['REMOTE_ADDR']
        url = "http://ip-api.com/json/" + ip_address
        headers = {
            'content-type': "application/json"
        }
        response = requests.request("GET", url, headers=headers)
        rec_data = response.json()
        vals['capture_gps_location'] = ip_address
        if rec_data and rec_data['status'] == "success":
            vals['capture_gps_location'] = str(rec_data['lat']) + "==" + str(rec_data['lon'])
            vals['latitude'] = str(rec_data['lat'])
            vals['longitute'] = str(rec_data['lon'])
        res = super(SaleorderLine, self).create(vals)
        return res

    @api.depends('order_id.state')
    def _compute_invoice_status(self):
        super(SaleorderLine, self)._compute_invoice_status()
        for line in self:
            # We handle the following specific situation: a physical product is partially delivered,
            # but we would like to set its invoice status to 'Fully Invoiced'. The use case is for
            # products sold by weight, where the delivered quantity rarely matches exactly the
            # quantity ordered.
            if line.order_id.sale_type == 'secondary_sales':
                line.invoice_status = 'invoiced'


    def _create_stock_move_manually(self, quantity, uom, group_id=False):
        """ TODO : When user select secondary sale the movement create from sale order is 
        distributor location to delar location
        """
        return True


    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        procurements = []
        for line in self:
            line = line.with_company(line.company_id)
            if line.state != 'sale' or not line.product_id.type in ('consu','product'):
                continue
            qty = line._get_qty_procurement(previous_product_uom_qty)
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty

            line_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
            if line.order_id.sale_type == 'secondary_sales':
                line._create_stock_move_manually(product_qty, procurement_uom, group_id)
            else:
                procurements.append(self.env['procurement.group'].Procurement(
                    line.product_id, product_qty, procurement_uom,
                    line.order_id.partner_shipping_id.property_stock_customer,
                    line.name, line.order_id.name, line.order_id.company_id, values))
        if procurements:
            self.env['procurement.group'].run(procurements)
        return True