# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
{
    'name': 'Travel',
    'version': '1.0',
    "category": '',
    'description': """
     Module to manage passenger transport.
    """,
    'author': '',
    'website': '',
    'depends': ['mail', 'fleet', 'stock', 'sale_management'],
    'data': [
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'data/payment_data.xml',
        'data/travel_data.xml',
        'views/partner_views.xml',
        'views/payment_views.xml',
        'views/vehicle_views.xml',
        'views/travel_views.xml',
        'views/travel_menu.xml',
        'views/tracking_view.xml',

    ],
    'demo_xml': [
    ],
    'test': [
    ],
    'installable': True,
}
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
