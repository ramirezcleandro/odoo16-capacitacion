# "from odoo import models, fields": Esta línea importa la clase "models" y el módulo "fields" de la
# biblioteca Odoo para poder definir modelos y campos en Odoo.
import base64
from io import BytesIO

import qrcode

from odoo import models, fields, api


# "class Library(models.Model):": Esta línea define una nueva clase llamada "Library" que hereda de la clase
# "Model" en Odoo, lo que indica que este será un modelo de datos en Odoo.
class Library(models.Model):
    # "_name = 'library.book'": Esta línea establece el nombre técnico del modelo como "library.book".
    # Este nombre se utiliza internamente en Odoo para referirse al modelo.
    _name = 'library.book'
    # "_description = 'Library Book'": Esta línea proporciona una descripción del modelo,
    # indicando que se trata de un libro de biblioteca. Esta descripción se mostrará en la interfaz de usuario de Odoo.
    _description = 'Library Book'
    # Ordenar por el campo 'name'
    _order = 'name'

    # En Odoo, los modelos y campos forman la base de la estructura de datos. Los modelos representan las entidades de
    # negocio, como clientes, productos o pedidos, y los campos definen los atributos de estas
    # entidades. Los campos en Odoo pueden ser de varios tipos, como Char (texto), Integer (número entero),
    # Float (número decimal), Boolean (verdadero/falso), Date (fecha), DateTime (fecha y hora), Selection
    # (selección), Many2one (relación a otro modelo), One2many (relación inversa a otro modelo), Many2many
    # (relación muchos a muchos), Binary (binario) y Monetary (monetario). Estas estructuras de datos son
    # fundamentales para definir cómo se almacena y se accede a la información en Odoo,
    # lo que permite personalizar y adaptar el sistema a las necesidades específicas de cada empresa.

    # cover_image (Binary): Almacena la imagen de portada del libro en formato binario
    cover_1920 = fields.Binary(string='Cover 1920', max_width=1920, max_height=1080)
    cover_128 = fields.Image("Cover 128", related="cover_1920", max_width=128, max_height=128, store=True)
    # name (Char): Almacena el título del libro como texto.
    name = fields.Char(string='Title', required=True)
    # author_id (Many2many): Permite seleccionar al autor del libro de una lista de socios.
    author_ids = fields.Many2many('res.partner', string='Author')
    # isbn (Char): Almacena el número de ISBN del libro como texto.
    isbn = fields.Char(string='ISBN')
    # description (Text): Permite ingresar una descripción más larga del libro como texto.
    description = fields.Text(string='Description')
    # year (Integer): Almacena el año de publicación del libro como un número entero.
    year = fields.Integer(string='Publication Year')
    # is_available (Boolean): Representa si el libro está disponible o no como un valor booleano.
    is_available = fields.Boolean(string='Is Available')
    # date_published (Date): Almacena la fecha de publicación del libro.
    date_published = fields.Date(string='Date Published')
    # currency_id (Many2one): Permite seleccionar la moneda asociada al campo monetario de una lista de monedas.
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id.id)
    # price (Float): Almacena el precio del libro como un número decimal.
    price = fields.Monetary(string='Price', currency_field='currency_id')
    # borrowing_hours (Float): Almacena la cantidad de horas que se pueden tomar prestado el libro como un número
    # decimal.
    borrowing_hours = fields.Float(string='Borrowing Hours')
    # category_id (Many2one): Permite seleccionar la categoría del libro de una lista de categorías.
    category_id = fields.Many2one('library.category', string='Category')

    bibliographic_reference_ids = fields.One2many('bibliographic.reference', 'book_id',
                                                  string='Bibliographic References')

    codigo_qr = fields.Binary(string='Código QR')

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if 'name' in vals:
            # Generar el código QR
            img = qrcode.make(vals['name'])
            buffer = BytesIO()
            img.save(buffer)
            qr_image = base64.b64encode(buffer.getvalue())
            record.write({'codigo_qr': qr_image})
        return record

    state = fields.Selection([
        ('out_of_stock', 'Out of stock'),
        ('in_stock', 'In stock')
    ], string='State', default='in_stock')

    # Este fragmento de código representa una restricción SQL en Odoo. En este caso, se está definiendo una restricción
    # llamada "book_uniq" que garantiza que el libro por autor debe ser único. La restricción se define como "unique
    # (author_id, name)", lo que significa que la combinación de "author_id" y "name"
    # debe ser única en la base de datos.
    # Si se intenta crear un registro que viole esta restricción, se generará un error con el mensaje
    # "The book per author must be unique." Esta restricción asegura que no se puedan crear registros duplicados
    # en la base de datos que tengan el mismo autor y nombre.
    _sql_constraints = [
        ('book_uniq', 'unique (author_ids, name)', "The book per author must be unique.")
    ]

    def action_set_out_of_stock(self):
        self.write({'state': 'out_of_stock'})

    def action_set_in_stock(self):
        self.write({'state': 'in_stock'})


class BibliographicReference(models.Model):
    _name = 'bibliographic.reference'
    _description = 'Bibliographic Reference'

    book_id = fields.Many2one('library.book', string='Book id')
    library_id = fields.Many2one('library.book', string='Library Book')
    title = fields.Char(string='Title', related='library_id.name')
    author_ids = fields.Many2many('res.partner', string='Author', related='library_id.author_ids')
    publication_date = fields.Date(string='Publication Date', related='library_id.date_published')
    isbn = fields.Char(string='ISBN', related='library_id.isbn')
    summary = fields.Text(string='Summary', related='library_id.description')
