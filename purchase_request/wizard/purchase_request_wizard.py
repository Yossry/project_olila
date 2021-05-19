# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class PurchaseRequestWizard(models.TransientModel):
    _name = 'purchase.request.wizard'

    department_ids = fields.Many2many('hr.department')

    def print_report(self):
        data = {}
        data['department_ids'] = self.department_ids.ids
        return self.env.ref('purchase_request.purchase_request_report_action').report_action(self, data=data)
