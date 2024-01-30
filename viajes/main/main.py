from odoo import http, fields
from odoo.http import request


class LibraryController(http.Controller):

    @http.route('/object/offer/create', methods=['POST'], auth='user', website=True)
    def create_book(self, **kw):
        payment_method_id = request.env['payment.method'].search([('name', '=', 'Electronico')], limit=1)
        service_type_id = request.env['product.product'].search([('name', '=', 'Entrega de producto comprado online')], limit=1)
        travel_type_id = request.env['travel.type'].search([('name', '=', 'National')], limit=1)
        if payment_method_id and service_type_id:
            request_id = request.env['travel.request'].search([('payment_method_id', '=', payment_method_id.id),
                                                               ('service_type_id', '=', service_type_id.id),
                                                               ('travel_type_id', '=', travel_type_id.id)
                                                               ], limit=1)
        else:
            request_id = False
        if request_id:
            vehicle_id = request.env['vehicle'].search([('for_carrie', '=', True)], limit=1)
        else:
            vehicle_id = False

        # Crear un nuevo registro de libro
        offer = request.env['travel.offer'].create({
            'travel_request_id': request_id,
            'vehicle_id': vehicle_id,
        })
        return offer
