# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models,_

class Driver(models.Model):
    _inherit = 'res.partner'

    nid = fields.Char('NID')
    is_driver = fields.Boolean(default=False)
    nature_driver = fields.Selection([
        ('driver','Driver'),
        ('helper','Helper'),
        ('third','3rd Party'),
        ], string="Type Of")
    license_number = fields.Char('License Number')
    license_upload = fields.Binary('License Upload')
    file_name = fields.Char("File Name")