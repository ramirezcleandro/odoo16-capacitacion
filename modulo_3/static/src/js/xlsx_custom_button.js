odoo.define('modulo_3.tree_button', function (require) { "use strict";

let Dialog = require('web.Dialog');
let ListController = require('web.ListController');
let ListView = require('web.ListView');
let viewRegistry = require('web.view_registry');
let DataExport = require('web.DataExport');
let framework = require('web.framework');
let pyUtils = require('web.py_utils');

let core = require('web.core');
let _t = core._t;

let CustomDataExport = DataExport.extend({

    _getExportData: function () {
        let exportedFields = this.defaultExportFields.map(field => ({
            name: field,
            label: this.record.fields[field].string,
            store: this.record.fields[field].store,
            type: this.record.fields[field].type,
        }));

        let idsToExport = false;
        if (_.isEmpty(exportedFields)) {
            Dialog.alert(this, _t("Please group the lines with some criteria..."));
            return;
        }

        if (this.isCompatibleMode) {
            exportedFields.unshift({ name: 'id', label: _t('External ID') });
        }

        framework.blockUI();
        this.getSession().get_file({
            url: '/web/export/' + 'xlsx_custom',
            data: {
                data: JSON.stringify({
                    model: this.record.model,
                    fields: exportedFields,
                    ids: idsToExport,
                    domain: this.domain,
                    groupby: this.groupby,
                    context: pyUtils.eval('contexts', [this.record.getContext()]),
                    import_compat: this.isCompatibleMode,
                })
            },
            complete: framework.unblockUI,
            error: (error) => this.call('crash_manager', 'rpc_error', error),
        });



    },
});

let TreeButton = ListController.extend({
   buttons_template: 'GAListView.buttons',
   events: _.extend({}, ListController.prototype.events, {
       'click .o_list_export_xlsx_2': '_onDirectExportDataMod',
   }),
   _onDirectExportDataMod() {
        let groupedBy = this.renderer.state.groupedBy;
        if (0 === groupedBy.length) {
            Dialog.alert(this, _t("Please select fields to export..."));
            return;
        }
        return this._rpc({model: 'ir.exports',
                          method: 'search_read',
                          args: [[], ['id']],limit: 1,}).then(() => this._getExportDialogWidgetMod()._getExportData())
    },
   _getExportDialogWidgetMod() {
        let state = this.model.get(this.handle);
        let defaultExportFields = this.renderer.columns.filter(field => field.tag === 'field' && state.fields[field.attrs.name].exportable !== true).map(field => field.attrs.name);
        let groupedBy = this.renderer.state.groupedBy;
        const domain = this.isDomainSelected && state.getDomain();
        return new CustomDataExport(this, state, defaultExportFields, groupedBy, domain, this.getSelectedIds());
    },

});



let GAListView = ListView.extend({
   config: _.extend({}, ListView.prototype.config, {
       Controller: TreeButton,
   }),
});

viewRegistry.add('export_xlsx2_tree', GAListView);

});