from odoo import models, fields, api


class PaymentMethod(models.Model):
    """
    Payment methods
    """
    _name = 'payment.method'

    name = fields.Char(required=True)

