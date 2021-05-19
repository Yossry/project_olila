# -*- coding: utf-8 -*-

from odoo import models,fields,api

class Committee(models.Model):

    _name = "committee.committee"
    _description = 'Committee'

    name = fields.Char(string="Name", copy=False, required=True)
    partner_id = fields.Many2one('res.users', string='Institute Head')
    manager_id = fields.Many2one('res.users', string='Committee Head')
    user_ids = fields.Many2many('res.users', string="Users")
    

class ResCompany(models.Model):
    _inherit = "res.company"

    approved_amount = fields.Float('Approved Amount')
