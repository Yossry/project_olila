# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date, datetime
import datetime as DT
import calendar



class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    _parent_name = "parent_id"
    _parent_store = True

    parent_path = fields.Char(index=True)
    type = fields.Selection([
        ('nsm', 'NSM'),
        ('rsm', 'RSM'),
        ('asm', 'ASM'),
        ('tso', 'TSO'),
        ('so', 'SO'),
    ], default="nsm", string='Type')
    target = fields.Float(compute='_compute_target', inverse='_set_target')
    sale_ids = fields.One2many('sale.order', 'responsible')
    history_lines = fields.One2many('target.history', 'emp_id')

    def _compute_target(self):
        current_month = fields.Datetime.today().month
        current_year = fields.Datetime.today().year
        for emp in self:
            if emp.type == 'so':
                target_line = emp.history_lines.filtered(lambda x: x.month == str(current_month) and x.year == str(current_year))
                emp.target = target_line and target_line.target or 0.0
            else:
                child_so = self.env['hr.employee'].search([('id', 'child_of', emp.id), ('type', '=', 'so')])
                emp.target = sum(child_so.mapped('target'))

    def _set_target(self):
        current_month = fields.Datetime.today().month
        current_year = fields.Datetime.today().year
        for emp in self:
            target_line = emp.history_lines.filtered(lambda x: x.month == str(current_month) and x.year == str(current_year))
            if emp.type == 'so':
                if target_line:
                    target_line.target = emp.target
                else:
                    self.env['target.history'].sudo().create({
                        'emp_id': emp.id,
                        'month': current_month,
                        'year': current_year,
                        'target': emp.target
                    })
            else:
                child_so = self.env['hr.employee'].search([('id', 'child_of', emp.id), ('type', '=', 'so')])
                total_count_so = len(child_so)
                for so in child_so:
                    if target_line:
                        target_line.target = emp.target / len(total_count_so)
                    else:
                        self.env['target.history'].sudo().create({
                            'emp_id': so.id,
                            'month': current_month,
                            'year': current_year,
                            'target': emp.target / len(total_count_so)
                        })

class TargetHistory(models.Model):
    _name = 'target.history'


    emp_id = fields.Many2one('hr.employee')
    month_name = fields.Char(compute='_compute_month_name', string="Month", store=True)
    month = fields.Char('Month No')
    year = fields.Char('Year')
    target = fields.Float('Target')
    archivement = fields.Float(compute='_compute_archivement', store=True)

    @api.depends('month', 'year')
    def _compute_month_name(self):
        for rec in self:
            if rec.month and rec.year:
                month = DT.date(int(rec.year), int(rec.month), 1).strftime('%B')
                rec.month_name = month
            else:
                rec.month_name = 'Undefined'

    @api.depends("emp_id.sale_ids", "emp_id.sale_ids.amount_total")
    def _compute_archivement(self):
        for rec in self:
            total_amount = 0.0
            start_date = fields.Datetime.today().replace(day=1, month=int(rec.month), year=int(rec.year) ,hour=0, minute=0, second=0)
            month_range = calendar.monthrange(int(rec.year), int(rec.month))
            date_end = fields.Datetime.today().replace(day=month_range[1],month=int(rec.month), year=int(rec.year), hour=11, minute=59, second=59)
            emp_id = rec.emp_id.id or False
            order_ids = self.env['sale.order'].search([('responsible', '=', emp_id) ,('date_order', '>', start_date), ('date_order', '<=', date_end)])
            total_amount = sum(line.amount_total for line in order_ids)
            rec.archivement = total_amount

    # Compute archivements and percentage 
