odoo.define('custom_list_view_manager.controller', function (require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');
    var localStorage = require('web.local_storage');
    var QWeb = core.qweb;
    var session = require('web.session');
    var Dialog = require('web.Dialog');
    var fieldUtils = require('web.field_utils');
    var ListController = require('web.ListController');
    var framework = require('web.framework');
    var view_registry = require('web.view_registry');
    var dom = require('web.dom');
    var bill_data = view_registry.get('account_tree');
    var basic_model = require('web.BasicModel');
    var ListView = require('web.ListView');
    var inventory_validate_button = view_registry.get('inventory_validate_button');
    var _t = core._t;

    ListController.include({

        saveRecord: function (ev) {
            var self = this;
            var def = this._super.apply(this, arguments);
            def.then(function () {
                self.custom_reload_list_view();
            });
            return def;
        },

        events: _.extend({}, ListController.prototype.events, {
            'click .refresh_button': 'custom_reload_list_view',
        }),

        custom_events: _.extend({}, ListController.prototype.custom_events, {
            custom_update_advance_search_renderer: "custom_update_advance_search_controller",
            enter_update_advance_search_renderer: "enter_update_advance_search_controller",
        }),

        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
        },


        custom_reload_list_view: function () {
            var custom_update_params = {};
            custom_update_params["modelName"] = this.modelName;
            custom_update_params["context"] = this.renderer.state.context;
            custom_update_params["ids"] = this.renderer.state.res_ids;
            custom_update_params["offset"] = this.renderer.state.offset;
            custom_update_params["currentId"] = this.renderer.state.res_id;
            custom_update_params["selectRecords"] = this.renderer.selection;
            custom_update_params["groupBy"] = this.renderer.state.groupedBy;
            custom_update_params["domain"] = this.renderer.state.domain;
            this.update(custom_update_params);

        },


        custom_update_advance_search_controller: function (custom_options) {
            var self = this;
            var custom_advance_search_params = {};
            custom_advance_search_params["modelName"] = self.renderer.state.model;
            custom_advance_search_params["context"] = self.renderer.state.context;
            custom_advance_search_params["ids"] = self.renderer.state.res_ids;
            custom_advance_search_params["offset"] = self.renderer.state.offset;
            custom_advance_search_params["currentId"] = self.renderer.state.res_id;
            custom_advance_search_params["selectRecords"] = self.renderer.selection
            custom_advance_search_params["groupBy"] = self.renderer.state.groupedBy
            custom_advance_search_params["domain"] = custom_options.data.updated_domain;
            self.update(custom_advance_search_params, undefined);
        },

        enter_update_advance_search_controller: function (cs_options) {
            var self = this;
            var custom_advance_search_params = {};
            custom_advance_search_params["modelName"] = self.renderer.state.model;
            custom_advance_search_params["context"] = self.renderer.state.context;
            custom_advance_search_params["ids"] = self.renderer.state.res_ids;
            custom_advance_search_params["offset"] = self.renderer.state.offset;
            custom_advance_search_params["currentId"] = self.renderer.state.res_id;
            custom_advance_search_params["selectRecords"] = self.renderer.selection
            custom_advance_search_params["groupBy"] = self.renderer.state.groupedBy
            if (self.renderer.state.domain.length === 0) {
                            custom_advance_search_params["domain"] = cs_options.data.domain_list
            } else {
                custom_advance_search_params["domain"] = self.renderer.state.domain.concat(cs_options.data.domain_list)
            }

            self.update(custom_advance_search_params, undefined);
        },


    });

    basic_model.include({
        _readGroup: function (list, options) {
            if(list.context.default_fields) list.fields = _.extend({},list.context.default_fields);
            return this._super.apply(this, arguments);
        },
    })

    return ListController;
});