import re
from datetime import datetime

import odoorpc
import requests

import zeep

from odoo import models, fields, api, _
from odoo.http import request, _logger


class TrackingPurchaseOrderLine(models.Model):
    _name = "tracking.purchase.order.line"
    _description = 'Tracking Purchase Order Line'
    _order = 'tracking_date desc'

    mantenedor_tracking_id = fields.Many2one('mantenedor.tracking')

    tracking_date = fields.Char('Tracking Date')

    status = fields.Selection([('other', 'Other'),
                               ('shipping', 'Shipping'),
                               ('accepted', 'Accepted'),
                               ('arrived', 'Arrived'),
                               ('departed', 'Departed'),
                               ('delivered', 'Delivered')], string='Status')

    status_massage = fields.Text('Status Message')

    country_id = fields.Many2one("res.country", string="Countries")

    city = fields.Char("Location")


class MantenedorTracking(models.Model):
    _name = "mantenedor.tracking"
    _description = "Get tracking mantenedor"

    name = fields.Char('Name')

    tracking = fields.Char(string='Tracking')

    internal_tracking = fields.Char(string='Internal Tracking')

    expected_location = fields.Char(string='Location')

    expected_date = fields.Char(string='Date')

    status_message = fields.Char(string='Status Message')

    destination = fields.Char(string='From destination')

    carriers = fields.Char(string='Carriers')

    toregion = fields.Char(string='To destination')

    externalTracking = fields.Char(string='External Tracking')

    parcelsapp_status = fields.Selection([('other', 'Other'),
                                          ('transit', 'Transit'),
                                          ('pickup', 'Available for Pickup'),
                                          ('delivered', 'Delivered')],
                                         string='Parcelsapp Status', default='other')

    done = fields.Boolean('Is done')

    days_in_transit = fields.Integer('Days in transit', default=0)

    parcelsapp_tracking_number = fields.Char(string='Parcelsapp Tracking Number')

    parcelsapp_api_key = fields.Text(string='Api Key', default=False)

    connection_status = fields.Boolean(string='Connection Status', default=True)

    error_message = fields.Text(string='Error Message')

    tracking_purchase_order_line_ids = fields.One2many('tracking.purchase.order.line', 'mantenedor_tracking_id')

    def create_offer(self):

        url = 'http://localhost:8069/jsonrpc'  # Reemplaza con la URL correcta de tu servidor JSON-RPC
        db = 'capacitacion'
        user = 'admin'
        password = 'admin'


        # Autenticación
        response = requests.post(url, json={
            "jsonrpc": 2.0,
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [db, user, password, {}]
            },
            "id": 0
        })
        auth_data = response.json()
        print(auth_data)

        if 'result' in auth_data and auth_data['result']:
            response = requests.post(url, json={
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute",
                    "args": [
                        db,
                        auth_data['result'],
                        password,
                        "payment.method",
                        "search_read",
                        [["name", "=", "Electronico"]], ["id"], 0, 3
                    ]
                }
            })
            data = response.json()
            payment_method_id = data['result'][0]['id']
            print(payment_method_id)
            response = requests.post(url, json={
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute",
                    "args": [
                        db,
                        auth_data['result'],
                        password,
                        "product.product",
                        "search_read",
                        [["name", "=", "Entrega de producto comprado online"]], ["id"], 0, 3
                    ]
                }
            })
            data = response.json()
            service_type_id = data['result'][0]['id']
            response = requests.post(url, json={
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute",
                    "args": [
                        db,
                        auth_data['result'],
                        password,
                        "travel.request",
                        "search_read",
                        [["payment_method_id", "=", payment_method_id],
                         ["service_type_id", "=", service_type_id]], ["id"], 0, 3
                    ]
                }
            })
            data = response.json()
            request_id = data['result'][0]['id']
            response = requests.post(url, json={
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute",
                    "args": [
                        db,
                        auth_data['result'],
                        password,
                        "vehicle",
                        "search_read",
                        [["for_carrie", "=", "True"]], ["id"], 0, 3
                    ]
                }
            })
            data = response.json()
            vehicle_id = data['result'][0]['id']
            response = requests.post(url, json={
                "jsonrpc": 2.0,
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute",
                    "args": [
                        db,
                        auth_data['result'],
                        password,
                        "travel.offer",
                        "create",
                        {
                            "travel_request_id": request_id,
                            "vehicle_id": vehicle_id,
                            "suggested_price": 100
                        }
                    ]
                },
                "id": 1
            })
            offer_data = response.json()
            print(offer_data)
        else:
            print("Autenticación fallida")

    @api.onchange('parcelsapp_status')
    def _onchange_parcelsapp_status(self):
        vals = {
            'purchase_parcelsapp_status': self.parcelsapp_status,
            'purchase_expected_location': self.expected_location
        }
        if self.parcelsapp_status == 'delivered':
            vals['status_new'] = 'destination'

    def _check_connection(self, message, status):
        self.sudo().write({
            'error_message': message,
            'connection_status': status
        })

    def check_connection(self, apiKey, trackingUrl, shipments):
        try:
            requests.post(trackingUrl, json={'apiKey': apiKey, 'shipments': shipments})
        except Exception as e:
            self._check_connection(str(e), False)
            _logger.error(str(e))
            return False
        self._check_connection('', True)
        return True

    def manual_track(self):
        for rec in self:
            apiKey = rec.parcelsapp_api_key
            trackingUrl = 'https://parcelsapp.com/api/v3/shipments/tracking'
            shipments = [{'trackingId': rec.tracking, 'language': 'es', 'country': 'Estados Unidos'}]
            check = self.check_connection(apiKey, trackingUrl, shipments)
            if not check:
                return False
            else:
                response = requests.post(trackingUrl, json={'apiKey': apiKey, 'shipments': shipments})
            response_json = response.json()
            if 'uuid' in response_json:
                uuid = response_json['uuid']
                response = requests.get(trackingUrl, params={'apiKey': apiKey, 'uuid': uuid})
            else:
                self._check_connection(_('The uuid did not arrive in the response.'), False)
            if response.status_code == 200:
                shipments = response.json().get('shipments', [])
                if not shipments:
                    return self._check_connection(
                        _('The shipments is empty, please review the Internal Tracking Number'), False)
                shipment = shipments[0]
                if 'error' in shipment:
                    error = shipment['error']
                    return self._check_connection(_('Shipments:' + ' ' + str(
                        error) + ' ' + 'Please review the tracking number or execute the manual tracking.'), False)
                external_tracking = shipment.get('externalTracking', [])
                if external_tracking:
                    external_tracking_url = external_tracking[0].get('url', '')
                    rec.externalTracking = external_tracking_url
                carriers = shipment.get('carriers', [])
                carriers_str = ', '.join(str(c) for c in carriers)
                rec.carriers = carriers_str
                status = shipment.get('status', '')
                if status == 'delivered':
                    rec.parcelsapp_status = 'delivered'
                elif status == 'transit':
                    rec.parcelsapp_status = 'transit'
                elif status == 'pickup':
                    rec.parcelsapp_status = 'pickup'
                attributes = shipment.get('attributes', [])
                for att in attributes:
                    if att['l'] == 'from':
                        packet_from_str = re.sub('\'|\[|\]', "", att['val'])
                        rec.destination = packet_from_str
                    elif att['l'] == 'to':
                        packet_to_str = re.sub('\'|\[|\]', "", att['val'])
                        rec.toregion = packet_to_str
                    elif att['l'] == 'days_transit':
                        rec.days_in_transit = int(att['val'])
                last_state = shipment.get('lastState', {})
                if 'date' in last_state:
                    string_to_data = re.sub("T", " ", last_state['date'])
                    rec.expected_date = string_to_data
                if 'done' in response_json:
                    done = response_json['done']
                    if done:
                        rec.done = True
                if 'location' in last_state:
                    location = last_state['location']
                    rec.expected_location = location
                if 'status' in last_state:
                    rec.status_message = last_state['status']
                if 'trackingId' in shipment:
                    rec.parcelsapp_tracking_number = shipment['trackingId']
                states = shipment.get('states', [])
                country_id = self.env["res.country"].search([("code", "=", "US")], limit=1)
                for state in states:
                    tracking_date_vals = state.get('date', False)
                    status_massage = state.get('status', '')
                    if 'Shipping' in status_massage:
                        status = 'shipping'
                    elif 'Accepted' in status_massage:
                        status = 'accepted'
                    elif 'Arrived' in status_massage:
                        status = 'arrived'
                    elif 'Departed' in status_massage:
                        status = 'departed'
                    elif 'Delivered' in status_massage:
                        status = 'delivered'
                    else:
                        status = 'other'
                    locations = state.get('location', '')
                    vals = {
                        'mantenedor_tracking_id': rec.id,
                        'tracking_date': tracking_date_vals,
                        'country_id': country_id.id,
                        'city': locations,
                        'status': status,
                        'status_massage': status_massage,
                    }
                    tracking_line = self.env["tracking.purchase.order.line"]
                    if not tracking_line.search([
                        ("mantenedor_tracking_id", "=", rec.id),
                        ("tracking_date", "=", tracking_date_vals),
                        ("country_id", "=", country_id.id),
                        ("status", "=", status),
                        ("status_massage", "=", status_massage)]):
                        tracking_line.sudo().create(vals)
                    else:
                        tracking_line.sudo().write(vals)
            elif response.status_code == 200 and 'error' in response_json:
                error = response_json['error']
                self._check_connection(_(str(error)), False)
            else:
                self._check_connection(_('Something went wrong with the request.'), False)

    def arrived(self):
        for mantenedor_tracking in self:
            mantenedor_tracking.write({'parcelsapp_status': 'delivered'})
            mantenedor_tracking.write({'done': True})
