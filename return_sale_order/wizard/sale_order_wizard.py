from odoo import models, fields, api, _

class SaleOrderWizard(models.TransientModel):
    _name = "sale.order.wizard"

    @api.model
    def default_get(self,fields):
        res = super(SaleOrderWizard,self).default_get(fields)
        active_id = self.env['sale.order'].browse(self.env.context.get('active_id'))
        picking_ids = active_id.mapped('picking_ids').filtered(lambda x: x.state in ('done') and x.picking_type_id.code == 'outgoing')
        if picking_ids:
            res.update({'picking_ids':[(6,0, picking_ids.ids)]})
        return res

    picking_ids = fields.Many2many('stock.picking', string='Pickings')
   
    def return_picking(self):
        for picking in self.picking_ids:
            vals = {'picking_id': picking.id, 'location_id' : picking.location_id.id}
            return_picking_wizard = self.env['stock.return.picking'].with_context(active_id=picking.id).create(vals)
            return_lines = []
            for line in picking.move_lines:
                return_line = self.env['stock.return.picking.line'].create({   
                        'product_id': line.product_id.id, 
                        'quantity': line.quantity_done, 
                        'wizard_id': return_picking_wizard.id,
                        'move_id': line.id})
                return_lines.append(return_line.id)
            return_picking_wizard.write({'product_return_moves': [(6, 0, return_lines)]})
            new_picking_id, pick_type_id = return_picking_wizard._create_returns()
            new_picking_ids = self.env['stock.picking'].browse(new_picking_id)
            new_picking_ids.action_assign()
        return True