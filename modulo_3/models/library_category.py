from odoo import models, fields


class LibraryCategory(models.Model):
    _name = 'library.category'
    _description = 'Library Category'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
