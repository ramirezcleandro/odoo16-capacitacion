# -*- coding: utf-8 -*-

from odoo import api

from odoo import models, fields


class PriceRange(models.Model):
    _name = 'price.range'
    _description = 'Price Range'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    price_level = fields.Selection([
        ('level1', 'Level 1'),
        ('level2', 'Level 2'),
        ('level3', 'Level 3')
    ], string='Price Level', default='level1')
    lower_price = fields.Monetary(string='Lower Price', currency_field='currency_id')
    upper_price = fields.Monetary(string='Upper Price', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency')
    range_type = fields.Selection([
        ('sales', 'Sales'),
        ('purchases', 'Purchases'),
        ('others', 'Others')
    ], string='Range Type', default='others')


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    price_ranges = fields.Many2many('price.range',
                                    string='Price Ranges',
                                    help='Select the applicable price ranges',
                                    domain="[('range_type', '=', 'purchases')]")

    upper_price_level = fields.Selection([
        ('all', 'All'),
        ('area_manager', 'Area Manager'),
        ('department_manager', 'Department Manager'),
        ('director', 'Director')
    ], string='Upper Price Level', compute='_compute_amount_total_dependent')

    @api.depends('order_line.price_total')
    def _compute_amount_total_dependent(self):
        for rec in self:
            if rec.price_ranges:
                for r in rec.price_ranges:
                    if r.lower_price < rec.amount_total < r.upper_price:
                        if r.price_level == 'level1':
                            rec.upper_price_level = 'area_manager'
                        elif r.price_level == 'level2':
                            rec.upper_price_level = 'department_manager'
                        elif r.price_level == 'level3':
                            rec.upper_price_level = 'director'
                        else:
                            rec.upper_price_level = 'all'
            else:
                rec.upper_price_level = 'all'

