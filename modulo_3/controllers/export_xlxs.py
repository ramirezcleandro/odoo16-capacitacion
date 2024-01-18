import json
import operator

from werkzeug.exceptions import InternalServerError

from odoo import http, _
from odoo.addons.web.controllers.export import ExportFormat, ExcelExport, GroupsTreeNode, GroupExportXlsxWriter
from odoo.http import content_disposition, request, _logger
from odoo.tools import html_escape, osutil


class GroupExportXlsxWriterCustom(GroupExportXlsxWriter):

    def write_group_custom(self, row, column, group_name, group, group_depth=0):
        group_name = group_name[1] if isinstance(group_name, tuple) and len(group_name) > 1 else group_name
        if group._groupby_type[group_depth] != 'boolean':
            group_name = group_name or _("Undefined")
        row, column = self._write_group_header_custom(row, column, group_name, group, group_depth)

        # Recursively write sub-groups
        for child_group_name, child_group in group.children.items():
            row, column = self.write_group_custom(row, column, child_group_name, child_group, group_depth + 1)

        # for record in group.data:
        #     row, column = self._write_row(row, column, record)
        return row, column

    def _write_group_header_custom(self, row, column, label, group, group_depth=0):
        aggregates = group.aggregated_values

        label = '%s%s (%s)' % ('    ' * group_depth, label, group.count)
        self.write(row, column, label, self.header_bold_style)
        for field in self.fields[1:]: # No aggregates allowed in the first column because of the group title
            column += 1
            aggregated_value = aggregates.get(field['name'])
            if field.get('type') == 'monetary':
                self.header_bold_style.set_num_format(self.monetary_format)
            elif field.get('type') == 'float':
                self.header_bold_style.set_num_format(self.float_format)
            else:
                aggregated_value = str(aggregated_value if aggregated_value is not None else '')
            self.write(row, column, aggregated_value, self.header_bold_style)
        return row + 1, 0


class ExportFormatCustom(ExportFormat):

    def from_group_data_custom(self, fields, rows):
        """ Conversion method from Odoo's export data to whatever the
        current export class outputs

        :params list fields: a list of fields to export
        :params list rows: a list of records to export
        :returns:
        :rtype: bytes
        """
        raise NotImplementedError()

    def base_custom(self, data):
        params = json.loads(data)
        model, fields, ids, domain, import_compat = \
            operator.itemgetter('model', 'fields', 'ids', 'domain', 'import_compat')(params)

        Model = request.env[model].with_context(import_compat=import_compat, **params.get('context', {}))
        if not Model._is_an_ordinary_table():
            fields = [field for field in fields if field['name'] != 'id']
        field_names = [f['name'] for f in fields]
        if import_compat:
            columns_headers = field_names
        else:
            columns_headers = [val['label'].strip() for val in fields]

        groupby = params.get('groupby')
        if not import_compat and groupby:
            groupby_type = [Model._fields[x.split(':')[0]].type for x in groupby]
            domain = [('id', 'in', ids)] if ids else domain
            groups_data = Model.read_group(domain, [x if x != '.id' else 'id' for x in field_names], groupby,
                                           lazy=False)

            # read_group(lazy=False) returns a dict only for final groups (with actual data),
            # not for intermediary groups. The full group tree must be re-constructed.
            tree = GroupsTreeNode(Model, field_names, groupby, groupby_type)
            for leaf in groups_data:
                tree.insert_leaf(leaf)

            response_data = self.from_group_data_custom(fields, tree)

            return request.make_response(response_data,
                                         headers=[('Content-Disposition',
                                                   content_disposition(
                                                       osutil.clean_filename(self.filename(model) + self.extension))),
                                                  ('Content-Type', self.content_type)],
                                         )


class ExcelExportCustom(ExportFormatCustom, ExcelExport):

    @http.route('/web/export/xlsx_custom', type='http', auth="user")
    def index_custom(self, data):
        try:
            return self.base_custom(data)
        except Exception as exc:
            _logger.exception("Exception during request handling.")
            payload = json.dumps({
                'code': 200,
                'message': "Odoo Server Error",
                'data': http.serialize_exception(exc)
            })
            raise InternalServerError(payload) from exc

    def from_group_data_custom(self, fields, groups):
        with GroupExportXlsxWriterCustom(fields, groups.count) as xlsx_writer:
            x, y = 1, 0
            for group_name, group in groups.children.items():
                x, y = xlsx_writer.write_group_custom(x, y, group_name, group)
        return xlsx_writer.value