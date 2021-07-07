# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Sayooj A O(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoice_count')
    operation_code = fields.Selection(related='picking_type_id.code')
    is_return = fields.Boolean()

    def _compute_invoice_count(self):
        """This compute function used to count the number of invoice for the picking"""
        for picking_id in self:
            move_ids = picking_id.env['account.move'].sudo().search([('invoice_origin', '=', picking_id.name)])
            if move_ids:
                self.invoice_count = len(move_ids)
            else:
                self.invoice_count = 0

    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        is_sale_auto_invoice = self.env['ir.config_parameter'].sudo().get_param('stock_move_invoice.is_sale_auto_invoice') or False
        is_purchase_auto_bill = self.env['ir.config_parameter'].sudo().get_param('stock_move_invoice.is_purchase_auto_bill') or False
        is_sale_auto_refund = self.env['ir.config_parameter'].sudo().get_param('stock_move_invoice.is_sale_auto_refund') or False
        is_purchase_auto_refund = self.env['ir.config_parameter'].sudo().get_param('stock_move_invoice.is_purchase_auto_refund') or False
        if not self.is_return and is_sale_auto_invoice and self.picking_type_id.code == 'outgoing':
            self.create_invoice()
        if is_purchase_auto_refund and self.picking_type_id.code == 'outgoing' and self.is_return:
            self.create_vendor_credit()
        if not self.is_return and  is_purchase_auto_bill and self.picking_type_id.code == 'incoming':
            self.create_bill()
        if is_sale_auto_refund and self.picking_type_id.code == 'incoming' and self.is_return:
            self.create_customer_credit()
        return res

    def create_invoice(self):
        for picking_id in self:
            current_user = self.env.uid
            customer_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param(
                'stock_move_invoice.customer_journal_id') or False
            if not customer_journal_id:
                raise UserError(_("Please configure the journal from settings"))
            invoice_line_list = []
            for move_ids_without_package in picking_id.move_ids_without_package:
                vals = (0, 0, {
                    'name': move_ids_without_package.description_picking,
                    'product_id': move_ids_without_package.product_id.id,
                    'price_unit': move_ids_without_package.product_id.lst_price,
                    'account_id': move_ids_without_package.product_id.property_account_income_id.id if move_ids_without_package.product_id.property_account_income_id
                    else move_ids_without_package.product_id.categ_id.property_account_income_categ_id.id,
                    'tax_ids': [(6, 0, [picking_id.company_id.account_sale_tax_id.id])],
                    'quantity': move_ids_without_package.quantity_done,
                })
                invoice_line_list.append(vals)
                invoice = picking_id.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'invoice_origin': picking_id.name,
                    'invoice_user_id': current_user,
                    'narration': picking_id.name,
                    'partner_id': picking_id.partner_id.id,
                    'currency_id': picking_id.env.user.company_id.currency_id.id,
                    'journal_id': int(customer_journal_id),
                    'payment_reference': picking_id.name,
                    'picking_id': picking_id.id,
                    'invoice_line_ids': invoice_line_list
                })
                return invoice

    def create_bill(self):
        for picking_id in self:
            current_user = self.env.uid
            vendor_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param(
                'stock_move_invoice.vendor_journal_id') or False
            if not vendor_journal_id:
                raise UserError(_("Please configure the journal from the settings."))
            invoice_line_list = []
            for move_ids_without_package in picking_id.move_ids_without_package:
                vals = (0, 0, {
                    'name': move_ids_without_package.description_picking,
                    'product_id': move_ids_without_package.product_id.id,
                    'price_unit': move_ids_without_package.product_id.lst_price,
                    'account_id': move_ids_without_package.product_id.property_account_income_id.id if move_ids_without_package.product_id.property_account_income_id
                    else move_ids_without_package.product_id.categ_id.property_account_income_categ_id.id,
                    'tax_ids': [(6, 0, [picking_id.company_id.account_purchase_tax_id.id])],
                    'quantity': move_ids_without_package.quantity_done,
                })
                invoice_line_list.append(vals)
                invoice = picking_id.env['account.move'].create({
                    'move_type': 'in_invoice',
                    'invoice_origin': picking_id.name,
                    'invoice_user_id': current_user,
                    'narration': picking_id.name,
                    'partner_id': picking_id.partner_id.id,
                    'currency_id': picking_id.env.user.company_id.currency_id.id,
                    'journal_id': int(vendor_journal_id),
                    'payment_reference': picking_id.name,
                    'picking_id': picking_id.id,
                    'invoice_line_ids': invoice_line_list
                })
                return invoice

    def create_customer_credit(self):
        """This is the function for creating customer credit note
                from the picking"""
        for picking_id in self:
            current_user = picking_id.env.uid
            customer_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param(
                'stock_move_invoice.customer_journal_id') or False
            if not customer_journal_id:
                raise UserError(_("Please configure the journal from settings"))
            invoice_line_list = []
            for move_ids_without_package in picking_id.move_ids_without_package:
                vals = (0, 0, {
                    'name': move_ids_without_package.description_picking,
                    'product_id': move_ids_without_package.product_id.id,
                    'price_unit': move_ids_without_package.product_id.lst_price,
                    'account_id': move_ids_without_package.product_id.property_account_income_id.id if move_ids_without_package.product_id.property_account_income_id
                    else move_ids_without_package.product_id.categ_id.property_account_income_categ_id.id,
                    'tax_ids': [(6, 0, [picking_id.company_id.account_sale_tax_id.id])],
                    'quantity': move_ids_without_package.quantity_done,
                })
                invoice_line_list.append(vals)
                invoice = picking_id.env['account.move'].create({
                    'move_type': 'out_refund',
                    'invoice_origin': picking_id.name,
                    'invoice_user_id': current_user,
                    'narration': picking_id.name,
                    'partner_id': picking_id.partner_id.id,
                    'currency_id': picking_id.env.user.company_id.currency_id.id,
                    'journal_id': int(customer_journal_id),
                    'payment_reference': picking_id.name,
                    'picking_id': picking_id.id,
                    'invoice_line_ids': invoice_line_list
                })
                return invoice

    def create_vendor_credit(self):
        """This is the function for creating refund
                from the picking"""
        for picking_id in self:
            current_user = self.env.uid
            vendor_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param(
                'stock_move_invoice.vendor_journal_id') or False
            if not vendor_journal_id:
                raise UserError(_("Please configure the journal from the settings."))
            invoice_line_list = []
            for move_ids_without_package in picking_id.move_ids_without_package:
                vals = (0, 0, {
                    'name': move_ids_without_package.description_picking,
                    'product_id': move_ids_without_package.product_id.id,
                    'price_unit': move_ids_without_package.product_id.lst_price,
                    'account_id': move_ids_without_package.product_id.property_account_income_id.id if move_ids_without_package.product_id.property_account_income_id
                    else move_ids_without_package.product_id.categ_id.property_account_income_categ_id.id,
                    'tax_ids': [(6, 0, [picking_id.company_id.account_purchase_tax_id.id])],
                    'quantity': move_ids_without_package.quantity_done,
                })
                invoice_line_list.append(vals)
                invoice = picking_id.env['account.move'].create({
                    'move_type': 'in_refund',
                    'invoice_origin': picking_id.name,
                    'invoice_user_id': current_user,
                    'narration': picking_id.name,
                    'partner_id': picking_id.partner_id.id,
                    'currency_id': picking_id.env.user.company_id.currency_id.id,
                    'journal_id': int(vendor_journal_id),
                    'payment_reference': picking_id.name,
                    'picking_id': picking_id.id,
                    'invoice_line_ids': invoice_line_list
                })
                return invoice

    def action_open_picking_invoice(self):
        """This is the function of the smart button which redirect to the
        invoice related to the current picking"""
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('invoice_origin', '=', self.name)],
            'context': {'create': False},
            'target': 'current'
        }


class StockReturnInvoicePicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        """in this function the picking is marked as return"""
        new_picking, pick_type_id = super(StockReturnInvoicePicking, self)._create_returns()
        picking = self.env['stock.picking'].browse(new_picking)
        picking.write({'is_return': True})
        return new_picking, pick_type_id
