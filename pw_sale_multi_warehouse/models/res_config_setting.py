# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_display_warehouse = fields.Boolean("Warehouse", implied_group='pw_sale_multi_warehouse.group_display_warehouse')
