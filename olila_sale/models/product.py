# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    master_carton_size = fields.Char(string="Master Carton Size")
    inner_carton_size = fields.Char(string="Inner Carton Size")