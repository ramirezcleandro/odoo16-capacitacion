from odoo import models, fields, api


class ObtainBookInformation(models.TransientModel):
    _name = 'obtain.book.information'
    _description = 'Obtain Book Information'

    book_id = fields.Many2one('library.book', string='Book')

    def get_book_info(self):
        # Implement the logic to retrieve information about the selected book
        selected_book = self.book_id
        # Llamar a la función JavaScript para obtener información del libro por su ID
        return {
            'type': 'ir.actions.client',
            'tag': 'web_external_js',
            'js_path': '/modulo_3/static/src/js/getBookInfo.js',
            'js_func': 'obtenerLibroPorId',
            'args': [selected_book.id],
        }
