from odoo import api, fields, models, _
from datetime import date, datetime

class Partner(models.Model):
    _inherit = 'res.partner'

    total_product_count = fields.Integer(compute='_total_product_count', string='Product')
    vendor_info_ids = fields.One2many('product.vendor.info', 'vendor_id', string="Vendor Info")

    # def _total_product_count(self):
    #     for rec in self:
    #         vendor_ids = self.env['product.vendor.info'].search([('vendor_id', '=', rec.id)])
    #         rec.total_product_count = len(vendor_ids.mapped('product_id').ids)

    # def view_vendor_info(self):
    #     vendor_ids = self.env['product.vendor.info'].search([('vendor_id', '=', self.id)])
    #     return {
    #         'name': _('Vendor Info'),
    #         'view_type': 'form',
    #         'view_mode': 'tree,form',
    #         'res_model': 'product.vendor.info',
    #         'view_id': False,
    #         'type': 'ir.actions.act_window',
    #         'domain': [('id', 'in', vendor_ids.ids)],
    #     }

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def prepare_vendar_info(self):
        product_info_ids = self.env['product.vendor.info'].search([])
        lists = []
        for line in self.order_line:
            if product_info_ids.filtered(lambda x: x.product_id.id == line.product_id.id and x.vendor_id.id == line.partner_id.id):
                for rec in product_info_ids.filtered(lambda x: x.product_id.id == line.product_id.id and x.vendor_id.id == line.partner_id.id):
                    rec.product_qty+=line.product_qty
            else :
                lists.append({
                'product_id' : line.product_id.id,
                'price_unit' : line.price_unit,
                'product_qty' : line.product_qty,
                'vendor_id' : line.partner_id.id,
                })
        return lists

    def button_confirm(self):
        result = super(PurchaseOrder,self).button_confirm()
        values = self.prepare_vendar_info()
        self.env['product.vendor.info'].create(values)
        return result

class ProductVendor(models.Model):
    _name="product.vendor.info"
    _description="Product Vendor"

    product_id = fields.Many2one('product.product', string="Product")
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure')
    vendor_id = fields.Many2one('res.partner', string="Vendor")


