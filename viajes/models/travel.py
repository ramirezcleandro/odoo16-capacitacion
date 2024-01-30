import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _


class Location(models.Model):
    _name = 'transport.location'
    # _inherit = ['mail.thread']

    client_id = fields.Many2one('res.partner', 'Client', track_visibility="onchange",
                                domain=[('is_driver', '=', False)]
                                , help='Client')
    name = fields.Char('Location name', track_visibility='onchange')
    longitude = fields.Float('Longitude', track_visibility='onchange')
    latitude = fields.Float('Latitude', track_visibility='onchange')
    address = fields.Text('Address')


class favorite_travel(models.Model):
    _name = 'favorite.travel'
    # _inherit = ['mail.thread']

    image_medium = fields.Binary(string="Imagen (medium)")

    name = fields.Char(help='Travel Name')

    client_id = fields.Many2one('res.partner', 'Client', track_visibility="onchange",
                                domain=[('is_driver', '=', False)]
                                , help='Client')

    travel = fields.Many2one('travel.request', 'Travel', track_visibility='onchange', help='Travel')


class favorite_driver(models.Model):
    _name = 'favorite.driver'
    # _inherit = ['mail.thread']

    name = fields.Char(string='Name', required=True, index=True, readonly=False, compute='_compute_name', store=True)
    client_id = fields.Many2one('res.partner', 'Client', track_visibility="onchange",
                                domain=[('is_driver', '=', False)]
                                , help='Client')

    driver_id = fields.Many2one('res.partner', 'Driver', track_visibility="onchange",
                                domain=[('is_driver', '=', True)]
                                , help='Driver of the vehicle', copy=False)

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'The record already exists!')
    ]

    @api.depends('client_id', 'driver_id')
    def _compute_name(self):
        for record in self:
            if record.client_id and record.driver_id:
                record.name = f"{record.client_id.name} - {record.driver_id.name}"
            else:
                record.name = False

    @api.model
    def create(self, vals):
        if 'driver_id' in vals:
            blocked_driver = self.env['block.driver'].search([('driver_id', '=', vals['driver_id'])])
            if blocked_driver:
                raise UserError(_('You cannot set this driver as favorite because it is blocked.'))
        return super().create(vals)

    def write(self, vals):
        if 'driver_id' in vals:
            blocked_driver = self.env['block.driver'].search([('driver_id', '=', vals['driver_id'])])
            if blocked_driver:
                raise UserError(_('You cannot set this driver as favorite because it is blocked.'))
        return super().write(vals)


class BlockDriver(models.Model):
    _name = 'block.driver'
    # _inherit = ['mail.thread']

    name = fields.Char(string='Name', required=True, index=True, readonly=False, compute='_compute_name', store=True)
    client_id = fields.Many2one('res.partner', 'Client', track_visibility="onchange",
                                domain=[('is_driver', '=', False)]
                                , help='Client')

    driver_id = fields.Many2one('res.partner', 'Driver', track_visibility="onchange",
                                domain=[('is_driver', '=', True)]
                                , help='Driver of the vehicle', copy=False)

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'The name must be unique!')
    ]

    @api.depends('client_id', 'driver_id')
    def _compute_name(self):
        for record in self:
            if record.client_id and record.driver_id:
                record.name = f"{record.client_id.name} - {record.driver_id.name}"
            else:
                record.name = False

    @api.model
    def create(self, vals):
        if 'driver_id' in vals:
            driver_id = vals['driver_id']
            favorite_travel = self.env['favorite.driver'].search([('driver_id', '=', driver_id)])
            if favorite_travel:
                favorite_travel.sudo().unlink()
        return super().create(vals)

    def write(self, vals):
        if 'driver_id' in vals:
            driver_id = vals['driver_id']
            favorite_travel = self.env['favorite.driver'].search([('driver_id', '=', driver_id)])
            if favorite_travel:
                favorite_travel.sudo().unlink()
        return super().write(vals)


class FavoriteTravel(models.Model):
    _name = 'block.client'
    # _inherit = ['mail.thread']

    driver_id = fields.Many2one('res.partner', 'Driver', track_visibility="onchange",
                                domain=[('is_driver', '=', True)]
                                , help='Driver of the vehicle', copy=False)

    client_id = fields.Many2one('res.partner', 'Client', track_visibility="onchange",
                                domain=[('is_driver', '=', False)]
                                , help='Client')


class Route(models.Model):
    _name = 'transport.route'
    _inherit = ['mail.thread']

    name = fields.Char('Route name', size=64, required=True, track_visibility='onchange')
    location_ids = fields.One2many('transport.route.location', 'route_id', 'Locations', track_visibility='onchange')


class RouteLocation(models.Model):
    _name = 'transport.route.location'
    _inherit = ['mail.thread']

    request_id = fields.Many2one('travel.request', 'Request', ondelete='cascade', track_visibility='onchange')
    travel_id = fields.Many2one('travel', 'Travel', ondelete='cascade', track_visibility='onchange')
    route_id = fields.Many2one('transport.route', 'Route', ondelete='cascade', track_visibility='onchange')
    location_id = fields.Many2one('transport.location', 'Location', track_visibility='onchange')
    # onchange
    longitude = fields.Float('Longitude', track_visibility='onchange')
    latitude = fields.Float('Latitude', track_visibility='onchange')
    address = fields.Text('Address', track_visibility='onchange')
    distance = fields.Float('Distance in meters', track_visibility='onchange')
    waiting_time = fields.Integer('Waiting time', track_visibility='onchange')
    pickup_time = fields.Datetime('Pickup time', track_visibility='onchange')
    arrival_time = fields.Datetime('Arrival time', track_visibility='onchange')


class ServiceType(models.Model):
    """
    Service type
    """
    _name = 'service.type'

    name = fields.Char(required=True)


class TravelType(models.Model):
    """
    Service type
    """
    _name = 'travel.type'

    name = fields.Char(required=True)


class TravelRequest(models.Model):
    """
    Travel requests
    """
    _name = 'travel.request'
    _inherit = ['mail.thread']
    _rec_name = 'travel_request_number'

    travel_request_number = fields.Char('Travel request number', size=16, readonly=True, track_visibility='onchange',
                                        default=lambda context: '/')
    client_id = fields.Many2one('res.partner', 'Client', required=True, track_visibility='onchange',
                                help='Travel client')
    location_ids = fields.One2many('transport.route.location', 'request_id', 'Locations', track_visibility='onchange')
    pets = fields.Boolean('Pets', track_visibility='onchange', help='Pets')
    at_service = fields.Boolean('At service', track_visibility='onchange')
    air_conditioning = fields.Boolean('Air conditioning', track_visibility='onchange')
    passengers_qty = fields.Integer('Passengers quantity', track_visibility='onchange')
    children = fields.Boolean('Children', track_visibility='onchange', help='Children')
    travel_type_id = fields.Many2one('travel.type', 'Travel type', track_visibility='onchange', help='Travel type')
    tour_type = fields.Selection(
        [('going', 'Going'), ('back', 'back'), ('going_back', 'Round'), ('route', 'Ruta'), ('circuit', 'Circuit')],
        'Tour type', required=True, track_visibility='onchange', help='Tour type')
    # Falta la lista de locations
    payment_method_id = fields.Many2one('payment.method', 'Payment Method', track_visibility='onchange', required=True,
                                        store=True)
    service_type_id = fields.Many2one('product.product',
                                      'Service type',
                                      track_visibility='onchange',
                                      required=True)

    # Falta dos campos del nombre y CI de la persona que va a viajar

    @api.model
    def create(self, vals):
        if ('travel_request_number' not in vals) or (vals.get('travel_request_number') == '/'):
            vals['travel_request_number'] = self.env['ir.sequence'].get(
                'travel.request')
        request = super(TravelRequest, self).create(vals)

        return request

    @api.onchange('location_ids')
    def _onchange_location_ids(self):
        for location in self.location_ids:
            if location.location_id:
                location.longitude = location.location_id.longitude
                location.latitude = location.location_id.latitude
                location.address = location.location_id.address


class TravelOffer(models.Model):
    """
    Travel offers
    """
    _name = 'travel.offer'
    _inherit = ['mail.thread']
    _rec_name = 'travel_offer_number'

    currency_id = fields.Many2one("res.currency",
                                  default=lambda self: self.env.user.company_id.currency_id,
                                  string="Currency",
                                  required=True)

    travel_offer_number = fields.Char('Travel offer number', size=16, readonly=True, track_visibility='onchange',
                                      default=lambda context: '/')

    travel_request_id = fields.Many2one('travel.request', 'Travel request', track_visibility='onchange', required=True)
    suggested_price = fields.Monetary('Suggested_price', track_visibility='onchange')
    driver_price = fields.Monetary('Driver price', track_visibility='onchange')
    pickup_time = fields.Integer('Estimated pickup time(min)', track_visibility='onchange')
    vehicle_id = fields.Many2one('vehicle', 'Vehicle', required=True, track_visibility='onchange', help='Vehicle')
    driver_id = fields.Many2one('res.partner', related='vehicle_id.driver_id', store=True)

    @api.model
    def create(self, vals):
        if ('travel_offer_number' not in vals) or (vals.get('travel_offer_number') == '/'):
            vals['travel_offer_number'] = self.env['ir.sequence'].get(
                'travel.offer')
        request = super(TravelOffer, self).create(vals)

        return request

    @api.onchange('driver_id', 'vehicle_id')
    def _onchange_driver_vehicle(self):
        if self.driver_id and self.vehicle_id.driver_id.id != self.driver_id.id:
            self.vehicle_id = False

    @api.onchange('driver_id')
    def _onchange_driver_id(self):
        if self.driver_id:
            vehicles = self.env['vehicle'].search([('driver_id', '=', self.driver_id.id)])
            if vehicles:
                self.vehicle_id = vehicles[0].id
            return {'domain': {'vehicle_id': [('id', 'in', vehicles.ids)]}}
        else:
            return {'domain': {'vehicle_id': []}}


class Travel(models.Model):
    """
    Travels
    """
    _name = 'travel'
    _rec_name = 'travel_number'
    _inherit = ['mail.thread']

    currency_id = fields.Many2one("res.currency",
                                  default=lambda self: self.env.user.company_id.currency_id,
                                  string="Currency",
                                  required=True)

    travel_number = fields.Char('Travel number', size=16, readonly=True, track_visibility='onchange',
                                default=lambda context: '/')

    travel_date = fields.Date('Travel date', required=True)

    location_ids = fields.One2many('transport.route.location', 'travel_id', 'Locations', track_visibility='onchange')
    travel_offer_id = fields.Many2one('travel.offer', 'Travel offer', required=True, track_visibility='onchange',
                                      help='Offer')
    client_id = fields.Many2one(related='travel_offer_id.travel_request_id.client_id', string='Client', required=True,
                                track_visibility='onchange', help='Client')
    driver_id = fields.Many2one(related='travel_offer_id.driver_id', string='Driver',
                                track_visibility='onchange', help='Driver', store=True)
    state = fields.Selection(
        [('created', 'Created'),
         ('processing', 'Processing'),
         ('test', 'Prueba'),
         ('cancelled', 'Cancelled'),
         ('abandoned', 'Abandoned'),
         ('ongoing', 'Ongoing'),
         ('completed', 'Completed')], 'State', default='created',
        track_visibility='onchange', help='State')
    price = fields.Monetary('Precio del viaje')
    # Solo para uso en el registro de log y creación de asientos contables
    performed_partner_id = fields.Many2one('res.partner', 'Performer', help='Performer')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    tm_order_id = fields.Char('Transfermovil payment order id')
    driver_comission_amount = fields.Monetary(
        string='Driver comission',
        compute='_get_travel_comissions',
        store=True
    )
    client_price = fields.Monetary(
        string='Paid',
        compute='_get_travel_comissions',
        store=True
    )
    client_devolution_amount = fields.Monetary(
        string='Client devolution',
        compute='_get_travel_comissions',
        default=0,
        store=True
    )
    aviaje_comission_amount = fields.Monetary(
        string='aViaje comission',
        compute='_get_travel_comissions',
        store=True
    )

    def action_processing(self):
        travelObj = self.env['travel']
        for rec in self:
            travels = travelObj.search([('client_id', '=', rec.client_id.id),
                                        ('driver_id', '=', rec.driver_id.id),
                                        ('state', 'in', ['processing', 'ongoing'])])
            if travels:
                raise UserError(_("You already have a trip in progress or on "
                                  "the way with the client: %s and the driver: %s.") %
                                (rec.client_id.display_name, rec.driver_id.display_name))

        self.write({'state': 'processing'})
        self._get_travel_comissions()
        return True

    def action_test(self):
        self.write({'state': 'test'})
        return True

    def action_cancelled(self):
        self.write({'state': 'cancelled'})
        self._get_travel_comissions()
        return True

    def action_abandoned(self):
        self.write({'state': 'abandoned'})
        self.env['sale.order'].action_cancel()
        self._get_travel_comissions()
        return True

    def action_ongoing(self):
        sale_order_vals = {
            'partner_id': self.client_id.id,
            'date_order': self.travel_date,
            'order_line': [
                (0, 0, {
                    'product_id': self.travel_offer_id.travel_request_id.service_type_id.id,
                    'product_uom_qty': 1,
                    'price_unit': self.travel_offer_id.driver_price,
                }),
            ],
        }
        self.env['sale.order'].create(sale_order_vals)
        self.write({'state': 'ongoing'})
        self._get_travel_comissions()
        return True

    def action_completed(self):
        self.write({'state': 'completed'})
        return True

    @api.constrains('client_id', 'driver_id')
    def _check_partners(self):
        for travel in self:
            if travel.client_id == travel.driver_id:
                raise ValidationError(_("Client and driver cannot be the same person."))

    @api.onchange('location_ids')
    def _onchange_location_ids(self):
        for location in self.location_ids:
            if location.location_id:
                location.longitude = location.location_id.longitude
                location.latitude = location.location_id.latitude
                location.address = location.location_id.address

    @api.model
    def create(self, vals):
        logObj = self.env['state.travel.log']

        if ('travel_number' not in vals) or (vals.get('travel_number') == '/'):
            vals['travel_number'] = self.env['ir.sequence'].get(
                'travel')

        travel = super(Travel, self).create(vals)

        logObj.create({
            'travel_id': travel.id,
            'state': 'created',
            'performed_partner_id': 1,
            'time': datetime.datetime.now()
        })

        return travel

    end_travel_date = fields.Date(string='End Travel Date')

    def write(self, vals):
        if vals.get('state'):
            performed_partner_id = vals.get('performed_partner_id') and vals.get('performed_partner_id') or self.env.uid
            if vals.get('completed'):
                performed_partner_id = self.driver_id.id
            logObj = self.env['state.travel.log']
            logObj.create({
                'travel_id': self.id,
                'state': vals.get('state'),
                'performed_partner_id': performed_partner_id,
                'time': datetime.datetime.now()
            })
            # if 'state' in vals and vals['state'] in ['cancelled', 'abandoned', 'completed'] and not self.end_travel_date:
            #     vals['end_travel_date'] = datetime.date.today()
        return super(Travel, self).write(vals)

    def button_report(self):
        pass

    @api.depends('state')
    def _get_travel_comissions(self):
        company = self.env.user.company_id
        for rec in self:
            offer_driver_price = rec.travel_offer_id.driver_price
            if rec.state in ('processing', 'ongoing', 'completed'):
                driver_amount = company.completed_driver_gain * offer_driver_price / 100
                aviaje_amount = company.completed_aviaje_gain * offer_driver_price / 100
                service_amount = company.service_commission_amount

                rec.driver_comission_amount = driver_amount
                rec.client_price = offer_driver_price + service_amount
                rec.price = rec.client_price
                rec.aviaje_comission_amount = aviaje_amount + service_amount

            elif rec.state in ('cancelled', 'abandoned') and rec.payment_method_id.name == 'Cash':
                tax = company.cancellation_client_tax
                if rec.state == 'abandoned':
                    tax = company.abandoned_client_tax
                amount = (offer_driver_price * tax / 100) + company.service_commission_amount

                driver_amount = company.cancellation_driver_gain * amount / 100
                aviaje_amount = company.cancellation_aviaje_gain * amount / 100
                rec.driver_comission_amount = 0.00
                # rec.client_devolution_amount = offer_driver_price - offer_driver_price * tax / 100?
                rec.client_devolution_amount = 0
                rec.aviaje_comission_amount = aviaje_amount + driver_amount

            elif rec.state in ('cancelled', 'abandoned') and rec.payment_method_id.name != 'Cash':
                tax = company.cancellation_client_tax
                if rec.state == 'abandoned':
                    tax = company.abandoned_client_tax
                amount = (offer_driver_price * tax / 100) + company.service_commission_amount
                travel_price = offer_driver_price + company.service_commission_amount

                if rec.performed_partner_id.id != rec.driver_id.id:
                    driver_amount = company.cancellation_driver_gain * amount / 100
                    aviaje_amount = company.cancellation_aviaje_gain * amount / 100
                    rec.driver_comission_amount = driver_amount
                    # rec.client_devolution_amount = offer_driver_price - offer_driver_price * tax / 100?
                    rec.client_devolution_amount = travel_price - (driver_amount + aviaje_amount)
                    rec.aviaje_comission_amount = aviaje_amount
                else:
                    rec.driver_comission_amount = 0.00
                    # rec.client_devolution_amount = offer_driver_price - offer_driver_price * tax / 100?
                    rec.client_devolution_amount = travel_price
                    rec.aviaje_comission_amount = 0.00


class ClientSeal(models.Model):
    """
    Payment methods
    """
    _name = 'pool.seal'

    name = fields.Char(required=True)


class TravelPoll(models.Model):
    """
    Travel polls
    """
    _name = 'travel.poll'
    _inherit = ['mail.thread']
    _rec_name = 'travel_id'

    travel_id = fields.Many2one('travel', 'Travel', required=True, track_visibility='onchange')
    evaluator_id = fields.Many2one('res.partner', 'Evaluator', required=True, track_visibility='onchange',
                                   help='Evaluator')
    evaluated_id = fields.Many2one('res.partner', 'Evaluated', required=True, track_visibility='onchange',
                                   help='Evaluated')

    quantitative_clasification = fields.Selection([('0', '0'),
                                                   ('1', '1'),
                                                   ('2', '2'),
                                                   ('3', '3'),
                                                   ('4', '4'),
                                                   ('5', '5')
                                                   ],
                                                  string='Quantitative Clasification', default='0')

    quantitative_assessment = fields.Integer('Quantitative assessment', track_visibility='onchange',
                                             help='Quantitative assessment')

    @api.onchange('travel_id', 'evaluator_id', 'evaluated_id')
    def _onchange_travel(self):
        pollObj = self.env['travel.poll']
        for rec in self:
            poll_exists = pollObj.search([('travel_id', '>=', rec.travel_id.id),
                                          ('evaluator_id', '<=', rec.evaluator_id.id),
                                          ('evaluated_id', '=', rec.evaluated_id.id)])
            if poll_exists:
                raise UserError(_("There is already a survey on this same travel, with the "
                                  "evaluator and the evaluated."))

    @api.onchange('quantitative_clasification')
    def _get_quantitative_clasification(self):
        for rec in self:
            rec.quantitative_assessment = int(rec.quantitative_clasification)

    qualitative_assessment = fields.Char('Qualitative assessment', track_visibility='onchange',
                                         help='Qualitative assessment')
    seal_ids = fields.Many2many('pool.seal', string='Seals', track_visibility='onchange', help="Seals")
    evaluated_vehicle_id = fields.Many2one(related='travel_id.travel_offer_id.vehicle_id', string="Vehicle",
                                           track_visibility='onchange', help='Evaluated vehicle', store=True,
                                           ondelete='cascade')

    is_client_poll = fields.Boolean('Is client poll', track_visibility='onchange', help='Is client poll')

    comfort_clasification = fields.Selection([('0', '0'),
                                              ('1', '1'),
                                              ('2', '2'),
                                              ('3', '3'),
                                              ('4', '4'),
                                              ('5', '5')
                                              ],
                                             string='Comfort Quantitative Clasification', default='0')

    comfort_quantitative_assessment = fields.Integer('Comfort quantitative assessment', track_visibility='onchange',
                                                     help='Comfort quantitative assessment')

    @api.onchange('comfort_clasification')
    def _get_comfort_quantitative(self):
        for rec in self:
            rec.comfort_quantitative_assessment = int(rec.comfort_clasification)

    comfort_qualitative_assessment = fields.Char('Comfort qualitative assessment', track_visibility='onchange',
                                                 help='Comfort qualitative assessment')

    @api.onchange('is_client_poll')
    def _get_is_client_poll(self):
        for rec in self:
            rec.comfort_clasification = '0'
            rec.comfort_quantitative_assessment = 0
            rec.comfort_qualitative_assessment = ''

    @api.constrains('evaluator_id', 'evaluated_id')
    def _check_partners(self):
        for poll in self:
            if poll.evaluator_id == poll.evaluated_id:
                raise ValidationError(_("Evaluator and evaluated person cannot be the same person."))


class StateTravelLog(models.Model):
    """
    State travel log
    """
    _name = 'state.travel.log'

    travel_id = fields.Many2one('travel', 'Travel', required=True, ondelete='cascade')
    state = fields.Selection(
        [('created', 'Created'),
         ('processing', 'Processing'),
         ('test', 'Prueba'),
         ('cancelled', 'Cancelled'),
         ('abandoned', 'Abandoned'),
         ('ongoing', 'Ongoing'),
         ('completed', 'Completed')], 'State', default='created', required=True, help='State')
    time = fields.Datetime(required=True)
    performed_partner_id = fields.Many2one('res.partner', 'Performer', help='Performer')
    description = fields.Text('Description')
