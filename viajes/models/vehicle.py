from odoo import models, fields, api, tools


class Vehicle(models.Model):
    """
    Vehicles
    """
    _name = 'vehicle'

    # Multi Company Rule
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)

    name = fields.Char(compute="_compute_vehicle_name", store=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True, help='Model of the vehicle')
    license_plate = fields.Char('License plate', related='vehicle_id.license_plate')
    model_id = fields.Many2one('fleet.vehicle.model', related='vehicle_id.model_id')
    air_conditioning = fields.Boolean('Air conditioning')
    driver_id = fields.Many2one('res.partner', related='vehicle_id.driver_id')
    color = fields.Char(related='vehicle_id.color')
    image = fields.Binary(related='vehicle_id.image_128', readonly=True)
    image_medium = fields.Binary(string="Logo (medium)")
    image_small = fields.Binary(string="Logo (small)")
    transport_id = fields.Many2one('conveyance', 'Conveyance')
    passengers_qty = fields.Integer('Passengers quantity')
    comfort_average = fields.Float(string="Comfort average", compute='_calc_qualification')
    for_carrie = fields.Boolean(string="Use for carrier")

    poll_ids = fields.One2many('travel.poll',
                               'evaluated_vehicle_id',
                               help='Vehicle polls',
                               domain=[('is_client_poll', '=', True)],
                               ondelete='cascade')

    def _calc_qualification(self):
        pollObj = self.env['travel.poll']
        for vehicle in self:
            qualification = 0
            pool_ids = pollObj.search([('evaluated_vehicle_id', '=', vehicle.id),
                                       ('is_client_poll', '=', True)])
            qty_pools = pollObj.search_count([('evaluated_vehicle_id', '=', vehicle.id),
                                              ('is_client_poll', '=', True)])
            for pool in pool_ids:
                qualification = qualification + pool.comfort_quantitative_assessment
            vehicle.comfort_average = qty_pools > 0 and qualification / qty_pools or qualification

    @api.depends('model_id.brand_id.name', 'model_id.name', 'license_plate')
    def _compute_vehicle_name(self):
        for record in self:
            if record.license_plate:
                record.name = record.model_id.brand_id.name + '/' + record.model_id.name + '/' + record.license_plate


class VehicleType(models.Model):
    """
    Vehicles
    """
    _name = 'vehicle.type'

    name = fields.Char(required=True)


class Conveyance(models.Model):
    _name = 'conveyance'

    name = fields.Char(required=True)
    vehicle_type_id = fields.Many2one('vehicle.type', 'Vehicle type', required=True)


class VehicleModel(models.Model):
    _name = 'vehicle.model'
    _description = 'Model of a vehicle'
    _order = 'name asc'

    name = fields.Char('Model name', required=True)
    brand_id = fields.Many2one('vehicle.brand', 'Brand', required=True, help='Brand of the vehicle')
    image = fields.Binary(related='brand_id.image', string="Logo")
    image_medium = fields.Binary(related='brand_id.image_medium', string="Logo (medium)")
    image_small = fields.Binary(related='brand_id.image_small', string="Logo (small)")


    @api.depends('name', 'brand_id')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.brand_id.name:
                name = record.brand_id.name + '/' + name
            res.append((record.id, name))
        return res

    @api.onchange('brand_id')
    def _onchange_brand(self):
        if self.brand_id:
            self.image_medium = self.brand_id.image
        else:
            self.image_medium = False


class VehicleBrand(models.Model):
    _name = 'vehicle.brand'
    _description = 'Brand of the vehicle'
    _order = 'name asc'

    name = fields.Char('Brand', required=True)
    image = fields.Binary("Logo", attachment=True,
                          help="This field holds the image used as logo for the brand, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized image", attachment=True,
                                 help="Medium-sized logo of the brand. It is automatically "
                                      "resized as a 128x128px image, with aspect ratio preserved. "
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True,
                                help="Small-sized logo of the brand. It is automatically "
                                     "resized as a 64x64px image, with aspect ratio preserved. "
                                     "Use this field anywhere a small image is required.")

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(VehicleBrand, self).create(vals)


    def write(self, vals):
        tools.image_resize_images(vals)
        return super(VehicleBrand, self).write(vals)
