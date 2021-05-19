# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_type = fields.Selection(selection=[('primary_sales', 'Primary Sales'),
        ('secondary_sales', 'Secondary Sales'), ('corporate_sales', 'Corporate Sales')], string="Sale Type")
    dealer_code = fields.Char(string="Dealer Code")
    estimation_lines = fields.One2many('cost.estimation', 'order_id', string="Estimation Details")

    def action_cost_estimation(self):
        return {
            'name': _('Cost Estimation'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cost.estimation',
            'view_id': self.env.ref('olila_sale.document_cost_estimation_form').id,
            'context': dict(order_id = self.id),
        }

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id.olila_type == 'dealer':
            self.dealer_code = self.partner_id.blila_code
        return super(SaleOrder, self).onchange_partner_id()


class SaleorderLine(models.Model):
    _inherit = 'sale.order.line'

    capture_gps_location = fields.Char(string="Capture GPS Location")
