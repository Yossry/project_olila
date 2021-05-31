from odoo import api, fields, models

class Picking(models.Model):
    _inherit = "stock.picking"

    def open_vehicle_distribution_management(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle Distributions',
            'view_mode': 'tree,form',
            'res_model': 'vehicle.distribution',
            'domain': [('picking_id', '=', self.id)],
            'context': {'default_picking_id': self.id}

        }

    def get_vehicle_distribution_count(self):
        self.vehicle_distribution_count = self.env['vehicle.distribution'].search_count([('picking_id', '=', self.id)])

    vehicle_distribution_count = fields.Integer(string='Vehicle Distributions', compute='get_vehicle_distribution_count')
    
    
    


