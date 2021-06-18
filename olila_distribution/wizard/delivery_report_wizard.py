# -*- coding: utf-8 -*-

from odoo import models,fields,api

class DeliveryReportWizard(models.TransientModel):
    _name = 'delivery.report.wizard'

    date_start = fields.Datetime(string="Start Date", required=True)
    date_end = fields.Datetime(string="End Date", required=True)

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
            },
        }
        return self.env.ref('olila_distribution.delivery_report').report_action(self, data=data)




class DeliveryReport(models.AbstractModel):

    _name = 'report.olila_distribution.delivery_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        delivery_orders = self.env['stock.picking'].search([('picking_type_code', '=', 'outgoing'), ('date_done', '>=', date_start),
                                                             ('date_done', '<=', date_end),('state', '=','done')])

        delivery_dict = {}

        for order in delivery_orders:
            distribution = self.env['vehicle.distribution'].search([('picking_id', '=', order.id ),('state', '=', 'approved')],limit = 1)
            if distribution.transport_type == 'own':
                vehicle_num = distribution.own_vehicle_id.license_plate
                driver_name = distribution.own_vehicle_driver_id.name
            else:
                vehicle_num = distribution.rent_vehicle_nbr
                # driver_name = distribution.rent_vehicle_driver
            total_product_qty = 0
            for line in order.sale_id.order_line:
                total_product_qty = total_product_qty + line.qty_delivered

            delivery_dict.setdefault(order, {'delivery_date': order.date_done, 'delivery_num': order.name, 'sale_num': order.sale_id.name,
                                              'sale_date': order.sale_id.date_order, 'vehicle_num': vehicle_num, 'driver_name': driver_name,
                                              'vehicle_type': distribution.transport_type, 'customer_name':order.sale_id.partner_id.name,
                                              'address': '', 'products':order.sale_id.order_line, 'total_qty':total_product_qty})



        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'date_start': date_start,
            'date_end': date_end,
            'delivery_dict': list(delivery_dict.values()),
            }
