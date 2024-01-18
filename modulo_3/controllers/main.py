from odoo import http, fields
from odoo.http import request


class LibraryController(http.Controller):

    @http.route('/create_book', auth='public', website=True)
    def create_book(self, **kw):
        # Buscar la categoría o crear una nueva si no existe
        category = request.env['library.category'].search([('name', '=', 'Nueva Categoria')], limit=1)
        if not category:
            category = request.env['library.category'].create({'name': 'Nueva Categoria'})

        # Crear un nuevo registro de libro
        request.env['library.book'].create({
            'name': 'Ejemplo de libro',
            'isbn': '1234567890',
            'description': 'Este es un ejemplo de libro creado desde el controlador.',
            'year': 2023,
            'is_available': True,
            'date_published': fields.Date.today(),
            'price': 29.99,
            'borrowing_hours': 72,
            'category_id': category.id
        })
        return "¡Libro creado con éxito!"

    @http.route('/get_book/<int:book_id>', auth='public', website=True)
    def get_book(self, book_id, **kw):
        # Buscar el registro de library.book por ID
        book = request.env['library.book'].browse(book_id)
        if book:
            return "Libro encontrado: {}".format(book.name)
        else:
            return "No se encontró ningún libro con el ID proporcionado."

    @http.route('/delete_book/<int:book_id>', auth='public', website=True)
    def delete_book(self, book_id, **kw):
        # Buscar y eliminar el registro de library.book por ID
        book = request.env['library.book'].search([('id', '=', book_id)])
        if len(book) >= 1:
            book.unlink()
            return "Libro eliminado con éxito."
        else:
            return "No se encontró ningún libro con el ID proporcionado."
