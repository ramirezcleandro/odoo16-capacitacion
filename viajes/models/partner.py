from odoo import models, fields, api
import xlsxwriter as xwr


class PartnerBadges(models.Model):
    """
    Partnet Badges
    """
    _name = 'partner.badges'

    partner_id = fields.Many2one('res.partner', string="Partner", required=True)
    seal_id = fields.Many2one('pool.seal', string="Seal")
    count = fields.Integer("Cant", default=0, compute='_get_count_seal')

    def _get_count_seal(self):
        pollObj = self.env['travel.poll']
        for rec in self:
            if rec.seal_id and rec.partner_id:
                cant = 0
                pool_ids = pollObj.search([('evaluated_id', '=', rec.partner_id.id)])
                for pool in pool_ids:
                    ids = []
                    for seal in pool.seal_ids:
                        ids.append(seal.id)
                    if rec.seal_id.id in ids:
                        cant = cant + 1
            rec.count = cant


class ServiceTypeDriver(models.Model):
    """
    Service type driver
    """
    _name = 'service.type.driver'

    name = fields.Char(required=True)


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    is_driver = fields.Boolean('Is Driver')
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='attachments_driver_rel',
        column1='partner_id',
        column2='attachment_id',
        string='Attached documents'
    )
    service_type_driver_ids = fields.Many2many('product.product', string='Driver service types')

    travel_type_ids = fields.Many2many('travel.type', 'travel_type_driver_rel', 'partner_id', 'travel_type_id',
                                       string='Driver travel types')

    available_average = fields.Float('Available average', track_visibility='onchange')
    points = fields.Integer(string="Points", compute='_calc_qualification')
    qualification = fields.Float(string="Qualification", compute='_calc_qualification')
    qty_finished_travels = fields.Integer(string="Qty finished travels", compute='_calc_qualification')
    availability_rate = fields.Float(string="Availability rate", compute='_calc_qualification')
    acceptance_rate = fields.Float(string="Acceptance rate", compute='_calc_qualification')
    cancellation_average = fields.Float('Cancellation average', compute='_calc_qualification',
                                        track_visibility='onchange')
    rejected_request_ids = fields.Many2many('travel.request', 'rejected_request_driver_rel', 'partner_id',
                                            'request_id', string='Reject requests by driver')
    rejected_request_after_offer_ids = fields.Many2many('travel.request', 'rejected_request_driver_rel', 'partner_id',
                                                        'request_id', string='Reject requests by driver after offer')
    category = fields.Char('Category')
    vehicle_ids = fields.One2many('vehicle', 'driver_id', string='Vehicles', readonly=True)
    document_revision_state = fields.Selection([('reviewing', 'Under review'), ('approved', 'Approved')],
                                               'Documents revision state', default='reviewing',
                                               track_visibility='onchange', help='Documents revision state')
    technical_review_expiration_date = fields.Date('Technical review expiration date')
    accepting_travels = fields.Boolean(
        string='Accepting travel requests', default=True, help='Indicates wether the driver is taking trips or not'
    )
    promotion_code = fields.Char('Promotion code')

    transport_location_ids = fields.One2many('transport.location',
                                             'client_id',
                                             string='Transport Location',
                                             ondelete="cascade")

    favorite_travel_ids = fields.One2many('favorite.travel',
                                          'client_id',
                                          string='Transport Travel',
                                          ondelete="cascade")

    favorite_driver_ids = fields.One2many('favorite.driver',
                                          'client_id',
                                          string='Transport Driver',
                                          ondelete="cascade")

    block_driver_ids = fields.One2many('block.driver',
                                       'client_id',
                                       string='Block Driver',
                                       ondelete="cascade")

    poll_ids = fields.One2many('travel.poll', 'evaluated_id', help='Vehicle polls')

    seal_list = fields.One2many('partner.badges', 'partner_id', help='Seal List', compute='_get_seal')

    def _get_seal(self):
        pollObj = self.env['travel.poll']
        sealObj = self.env['partner.badges']
        for rec in self:
            pool_ids = pollObj.search([('evaluated_id', '=', rec.id)])
            for pool in pool_ids:
                for seal in pool.seal_ids:
                    status = sealObj.search([('seal_id', '=', seal.id), ('partner_id', '=', rec.id)])
                    if not status:
                        vals = ({
                            'partner_id': rec.id,
                            'seal_id': seal.id
                        })
                        sealObj.create(vals)
            rec_ids = []
            list_ids = sealObj.search([('partner_id', '=', rec.id)])
            if list_ids:
                for ids in list_ids:
                    rec_ids.append(ids.id)
            if len(rec_ids) != 0:
                rec.seal_list = rec_ids
            else:
                rec.seal_list = False

    def _calc_qualification(self):
        travelObj = self.env['travel']
        offerObj = self.env['travel.offer']
        pollObj = self.env['travel.poll']
        for partner in self:
            qualification = 0
            qty_finished_travels = travelObj.search_count(
                [('driver_id', '=', partner.id), ('state', 'in', ('completed', 'posted'))])
            if not partner.is_driver:
                qty_finished_travels = travelObj.search_count(
                    [('client_id', '=', partner.id), ('state', 'in', ('completed', 'posted'))])
            qty_offers = offerObj.search_count([('driver_id', '=', partner.id)])
            # if not partner.is_driver:
            #     qty_offers = offerObj.search_count([('client_id', '=', partner.id)])
            qty_travels = travelObj.search_count([('driver_id', '=', partner.id)])
            if not partner.is_driver:
                qty_travels = travelObj.search_count([('client_id', '=', partner.id)])
            qty_travels_cancelled = travelObj.search_count([('driver_id', '=', partner.id),
                                                            ('state', '=', 'cancelled'),
                                                            ('performed_partner_id', '=', partner.id)])
            if not partner.is_driver:
                qty_travels_cancelled = travelObj.search_count(
                    [('client_id', '=', partner.id),
                     ('state', '=', 'cancelled')])
            qty_requests = len(partner.rejected_request_ids) + qty_offers
            qty_requests_after_offer = len(partner.rejected_request_after_offer_ids) + qty_travels
            if qty_requests > 0:
                partner.availability_rate = qty_offers * 100 / qty_requests
            else:
                partner.availability_rate = 0
            if qty_requests_after_offer > 0:
                partner.acceptance_rate = qty_travels * 100 / qty_requests_after_offer
            else:
                partner.acceptance_rate = 0
            if qty_travels > 0:
                partner.cancellation_average = qty_travels_cancelled * 100 / qty_travels
            else:
                partner.cancellation_average = 0
            partner.qty_finished_travels = qty_finished_travels
            partner.points = qty_finished_travels
            pool_ids = pollObj.search([('evaluated_id', '=', partner.id)])
            qty_pools = pollObj.search_count([('evaluated_id', '=', partner.id)])
            for pool in pool_ids:
                qualification = qualification + pool.quantitative_assessment
            partner.qualification = qty_pools > 0 and qualification / qty_pools or qualification

    def button_enable(self):
        for rec in self:
            rec.write({'active': True})

    def button_disable(self):
        for rec in self:
            rec.write({'active': False})
