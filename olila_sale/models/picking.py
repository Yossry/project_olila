# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Picking(models.Model):
    _inherit = 'stock.picking'

    fleet_id = fields.Many2one('fleet.vehicle', string="Vehicle")
