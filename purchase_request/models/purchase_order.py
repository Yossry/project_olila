# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # approval = fields.Boolean(compute='_compute_order_approval')
    # approval_line_ids = fields.One2many('order.approval.line', 'res_id')

    # def _compute_order_approval(self):
    #     for order in self:
    #         approval_line = self.env['order.approval.line'].search([
    #             ('res_model', '=', 'purchase.order'),
    #             ('res_id', '=', order.id),
    #             ('member_id', '=', self.env.user.id)])
    #         order.approval = True if not approval_line else approval_line.approval

    # @api.model
    # def create(self, vals):
    #     rec = super(PurchaseOrder, self).create(vals)
    #     if 'requisition_id' in vals and vals.get('requisition_id'):
    #         requisition_id = self.env['purchase.requisition'].browse(vals.get('requisition_id'))
    #         committee = requisition_id.purchase_request_id.team_id
    #         if committee and committee.manager_id:
    #             for member in committee.user_ids | committee.manager_id:
    #                 self.env['order.approval.line'].create({
    #                     'member_id': member.id,
    #                     'res_model': self._name,
    #                     'res_id': rec.id,
    #                 })
    #     return rec

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
                    or order.user_has_groups('purchase_request.group_principal') or order.user_has_groups('purchase_request.group_comitee_head'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})

        approval_lines = self.env['order.approval.line'].search([
            ('res_model', '=', 'purchase.order'),
            ('res_id', 'in', self.ids)])

        if not all([line.approval for line in approval_lines]):
            raise UserError(_('You needs approval of all committee members'))
        else:
            approval_lines.unlink()
        return True

    def button_order_approval(self):
        approval_line = self.env['order.approval.line'].search([
            ('res_model', '=', 'purchase.order'),
            ('res_id', '=', self.id),
            ('member_id', '=', self.env.user.id)])
        approval_line.write({'approval': True})
        return True

class OrderApprovalLine(models.Model):
    _name = 'order.approval.line'
    _rec_name = 'member_id'

    member_id = fields.Many2one('res.users', string='Member')
    approval = fields.Boolean('Approval')
    res_model = fields.Char('Related Model ID')
    res_id = fields.Many2one('purchase.order', 'Related Document ID')
