# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    cancellation_client_tax = fields.Float(string="Cancellation client tax", default=10)
    abandoned_client_tax = fields.Float(string="Abandoned client tax", default=25)
    cancellation_driver_gain = fields.Float(string="Cancellation driver gain", default=75)
    cancellation_aviaje_gain = fields.Float(string="Cancellation aviaje gain", default=25)
    service_commission_amount = fields.Float(string="Service commission", default=25)
    completed_driver_gain = fields.Float(string="Completed driver gain", default=90)
    completed_aviaje_gain = fields.Float(string="Completed aviaje gain", default=10)
    transfermovil_commission_percent = fields.Float(string="Transfermovil commission percent", default=1.5)
    extra_time_commission_percent = fields.Float(string="Extra Time commission percent", default=25)

