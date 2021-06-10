# -*- coding: utf-8 -*-
from odoo import fields, models


class Settings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_journal_id = fields.Many2one('account.journal', string='Customer Journal',
                                          config_parameter='stock_move_invoice.customer_journal_id')
    vendor_journal_id = fields.Many2one('account.journal', string='Vendor Journal',
                                        config_parameter='stock_move_invoice.vendor_journal_id')
    is_sale_auto_invoice = fields.Boolean(string="Auto Invoice", config_parameter='stock_move_invoice.is_sale_auto_invoice')
    is_sale_auto_refund = fields.Boolean(string="Auto Refund", config_parameter='stock_move_invoice.is_sale_auto_refund')
    is_purchase_auto_bill = fields.Boolean(string="Auto Bill", config_parameter='stock_move_invoice.is_purchase_auto_bill')
    is_purchase_auto_refund = fields.Boolean(string="Auto Refund", config_parameter='stock_move_invoice.is_purchase_auto_refund')