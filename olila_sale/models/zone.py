# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Zone(models.Model):
    _name = 'res.zone'
    _description = 'Zone'
    _inherit = ['format.address.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", copy=False)