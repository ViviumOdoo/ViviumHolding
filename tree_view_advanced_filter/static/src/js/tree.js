odoo.define('tree_view_advanced_filter.tree', function(require) {
    "use strict";
    var localStorage = require('web.local_storage');
    var time = require('web.time');

    var AbstractModel = require('web.AbstractModel');
    var Context = require('web.Context');
    var field_utils = require('web.field_utils');
    var session = require('web.session');
    var ListRenderer = require('web.ListRenderer');
    var BasicRenderer = require('web.BasicRenderer');
    var datepicker = require('web.datepicker');
    var config = require('web.config');
    var core = require('web.core');
    var dom = require('web.dom');
    var field_utils = require('web.field_utils');
    var listCont = require('web.ListController');
    var Pager = require('web.Pager');
    var utils = require('web.utils');
    const {
        str_to_datetime
    } = require('web.time');
    var time = require('web.time');
    var model;
    var domain;
    var authorizedValues = {};

    var ListRendererCust = ListRenderer.include({
        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            model = state.model
            localStorage.setItem('domainlist', JSON.stringify([]));
            domain = state.domain

        },
        events: _.extend({}, ListRenderer.prototype.events, {
            'keyup thead tr td.search_td input': '_onfilter',
            'click .search_button': '_onSearch',
            'click .remove_button': '_onRemove',
            'keypress  thead tr td': '_onKeyPress',
        }),

        _getRecordID: function (rowIndex) {
            if(!this.hasSelectors){
            var rowIndex = rowIndex +1
            var $tr = this.$('table.o_list_table > tbody tr.o_data_row').eq(rowIndex);
            }else{
                var $tr = this.$('table.o_list_table > tbody tr').eq(rowIndex);
            }
            return $tr.data('id');
        },

        confirmUpdate: function(state, id, fields, ev) {
            var self = this;

            var oldData = this.state.data;
            this.state = state;
            return this.confirmChange(state, id, fields, ev).then(function() {
                // If no record with 'id' can be found in the state, the
                // confirmChange method will have rerendered the whole view already,
                // so no further work is necessary.
                var record = self._getRecord(id);
                if (!record) {
                    return;
                }

                _.each(oldData, function(rec) {
                    if (rec.id !== id) {
                        self._destroyFieldWidgets(rec.id);
                    }
                });

                // re-render whole body (outside the dom)
                self.defs = [];
                var $newBody = self._renderBody();
                var defs = self.defs;
                delete self.defs;

                return Promise.all(defs).then(function() {
                    // update registered modifiers to edit 'mode' because the call to
                    // _renderBody set baseModeByRecord as 'readonly'
                    _.each(self.columns, function(node) {
                        self._registerModifiers(node, record, null, {
                            mode: 'edit'
                        });
                    });

                    // store the selection range to restore it once the table will
                    // be re-rendered, and the current cell re-selected
                    var currentRowID;
                    var currentWidget;
                    var focusedElement;
                    var selectionRange;
                    if (self.currentRow !== null) {
                        currentRowID = self._getRecordID(self.currentRow);
                        currentWidget = self.allFieldWidgets[currentRowID][self.currentFieldIndex];
                        if (currentWidget) {
                            focusedElement = currentWidget.getFocusableElement().get(0);
                            if (currentWidget.formatType !== 'boolean') {
                                selectionRange = dom.getSelectionRange(focusedElement);
                            }
                        }
                    }

                    // remove all data rows except the one being edited, and insert
                    // data rows of the re-rendered body before and after it
                    var $editedRow = self._getRow(id);
                    $editedRow.nextAll('.o_data_row').remove();
                    $editedRow.prevAll('.o_data_row').remove();
                    var $newRow = $newBody.find('.o_data_row[data-id="' + id + '"]');
                    $newRow.prevAll('.o_data_row').get().reverse().forEach(function(row) {
                        $(row).insertBefore($editedRow);
                    });
                    $newRow.nextAll('.o_data_row').get().reverse().forEach(function(row) {
                        $(row).insertAfter($editedRow);
                    });

                    if (self.currentRow !== null) {
                        var newRowIndex = $editedRow.prop('rowIndex') - 2;
                        self.currentRow = newRowIndex;
                        return self._selectCell(newRowIndex, self.currentFieldIndex, {
                                force: true
                            })
                            .then(function() {
                                // restore the selection range
                                currentWidget = self.allFieldWidgets[currentRowID][self.currentFieldIndex];
                                if (currentWidget) {
                                    focusedElement = currentWidget.getFocusableElement().get(0);
                                    if (selectionRange) {
                                        dom.setSelectionRange(focusedElement, selectionRange);
                                    }
                                }
                            });
                    }
                });
            });
        },
        editFirstRecord: function(ev) {
            const $borderRow = this._getBorderRow(ev.data.side || 'first');
            this._selectCell($borderRow.prop('rowIndex') - 2, ev.data.cellIndex || 0);
        },

        removeLine: function(state, recordID) {
            this.state = state;
            var $row = this._getRow(recordID);
            if ($row.length === 0) {
                return;
            }
            if ($row.prop('rowIndex') - 2 === this.currentRow) {
                this.currentRow = null;
                this._enableRecordSelectors();
            }

            // destroy widgets first
            this._destroyFieldWidgets(recordID);
            // remove the row
            if (this.state.count >= 4) {
                $row.remove();
            } else {
                // we want to always keep at least 4 (possibly empty) rows
                var $emptyRow = this._renderEmptyRow();
                $row.replaceWith($emptyRow);
                // move the empty row we just inserted after last data row
                const $lastDataRow = this.$('.o_data_row:last');
                if ($lastDataRow.length) {
                    $emptyRow.insertAfter($lastDataRow);
                }
            }
        },
        _getNearestEditableRow: function ($row, next) {
        const direction = next ? 'next' : 'prev';
        let $nearestRow;
        if (this.editable) {
            $nearestRow = $row[direction]();
            if (!$nearestRow.hasClass('o_data_row')) {
                var $nextBody = $row.closest('tbody')[direction]();
                while ($nextBody.length && !$nextBody.find('.o_data_row').length) {
                    $nextBody = $nextBody[direction]();
                }
                $nearestRow = $nextBody.find(`.o_data_row:${next ? 'first' : 'last'}`);
            }
        } else {
            // In readonly lists, look directly into selected records
            const recordId = $row.data('id');
            const rowSelectionIndex = this.selection.indexOf(recordId);
            let nextRowIndex;
            if (rowSelectionIndex < 0) {
                nextRowIndex = next ? 0 : this.selection.length - 2;
            } else {
                nextRowIndex = rowSelectionIndex + (next ? 2 : -2);
            }
            // Index might be out of range, will then return an empty jQuery object
            $nearestRow = this._getRow(this.selection[nextRowIndex]);
        }
        return $nearestRow;
    },

        setRowMode: function(recordID, mode) {
            var self = this;
            var record = self._getRecord(recordID);
            if (!record) {
                return Promise.resolve();
            }

            var editMode = (mode === 'edit');
            var $row = this._getRow(recordID);
            this.currentRow = editMode ? $row.prop('rowIndex') - 2 : null;
            var $tds = $row.children('.o_data_cell');
            var oldWidgets = _.clone(this.allFieldWidgets[record.id]);

            // Prepare options for cell rendering (this depends on the mode)
            var options = {
                renderInvisible: editMode,
                renderWidgets: editMode,
            };
            options.mode = editMode ? 'edit' : 'readonly';

            // Switch each cell to the new mode; note: the '_renderBodyCell'
            // function might fill the 'this.defs' variables with multiple promise
            // so we create the array and delete it after the rendering.
            var defs = [];
            this.defs = defs;
            _.each(this.columns, function(node, colIndex) {
                var $td = $tds.eq(colIndex);
                var $newTd = self._renderBodyCell(record, node, colIndex, options);

                // Widgets are unregistered of modifiers data when they are
                // destroyed. This is not the case for simple buttons so we have to
                // do it here.
                if ($td.hasClass('o_list_button')) {
                    self._unregisterModifiersElement(node, recordID, $td.children());
                }

                // For edit mode we only replace the content of the cell with its
                // new content (invisible fields, editable fields, ...).
                // For readonly mode, we replace the whole cell so that the
                // dimensions of the cell are not forced anymore.
                if (editMode) {
                    $td.empty().append($newTd.contents());
                } else {
                    self._unregisterModifiersElement(node, recordID, $td);
                    $td.replaceWith($newTd);
                }
            });
            delete this.defs;

            // Destroy old field widgets
            _.each(oldWidgets, this._destroyFieldWidget.bind(this, recordID));

            // Toggle selected class here so that style is applied at the end
            $row.toggleClass('o_selected_row', editMode);
            if (editMode) {
                this._disableRecordSelectors();
            } else {
                this._enableRecordSelectors();
            }

            return Promise.all(defs).then(function() {
                // necessary to trigger resize on fieldtexts
                core.bus.trigger('DOM_updated');
            });
        },

        editRecord: function(recordID) {
            var $row = this._getRow(recordID);
            var rowIndex = $row.prop('rowIndex') - 2;
            this._selectCell(rowIndex, 0);
        },
        _moveToSideLine: function(next, options) {
            options = options || {};
            const recordID = this._getRecordID(this.currentRow);
            this.commitChanges(recordID).then(() => {
                const record = this._getRecord(recordID);
                const multiEdit = this.isInMultipleRecordEdition(recordID);
                if (!multiEdit) {
                    const fieldNames = this.canBeSaved(recordID);
                    if (fieldNames.length && (record.isDirty() || options.forceCreate)) {
                        // the current row is invalid, we only leave it if it is not dirty
                        // (we didn't make any change on this row, which is a new one) and
                        // we are navigating with TAB (forceCreate=false)
                        return;
                    }
                }
                // compute the index of the next (record) row to select, if any
                const side = next ? 'first' : 'last';
                const borderRowIndex = this._getBorderRow(side).prop('rowIndex') - 2;
                const cellIndex = next ? 0 : this.allFieldWidgets[recordID].length - 2;
                const cellOptions = {
                    inc: next ? 1 : -1,
                    force: true
                };
                const $currentRow = this._getRow(recordID);
                const $nextRow = this._getNearestEditableRow($currentRow, next);
                let nextRowIndex = null;
                let groupId;

                if (!this.isGrouped) {
                    // ungrouped case
                    if ($nextRow.length) {
                        nextRowIndex = $nextRow.prop('rowIndex') - 2;
                    } else if (!this.editable) {
                        nextRowIndex = borderRowIndex;
                    } else if (!options.forceCreate && !record.isDirty()) {
                        this.trigger_up('discard_changes', {
                            recordID: recordID,
                            onSuccess: this.trigger_up.bind(this, 'activate_next_widget', {
                                side: side
                            }),
                        });
                        return;
                    }
                } else {
                    // grouped case
                    var $directNextRow = $currentRow.next();
                    if (next && this.editable === "bottom" && $directNextRow.hasClass('o_add_record_row')) {
                        // the next row is the 'Add a line' row (i.e. the current one is the last record
                        // row of the group)
                        if (options.forceCreate || record.isDirty()) {
                            // if we modified the current record, add a row to create a new record
                            groupId = $directNextRow.data('group-id');
                        } else {
                            // if we didn't change anything to the current line (e.g. we pressed TAB on
                            // each cell without modifying/entering any data), we discard that line (if
                            // it was a new one) and move to the first record of the next group
                            nextRowIndex = ($nextRow.prop('rowIndex') - 2) || null;
                            this.trigger_up('discard_changes', {
                                recordID: recordID,
                                onSuccess: () => {
                                    if (nextRowIndex !== null) {
                                        if (!record.res_id) {
                                            // the current record was a new one, so we decrement
                                            // nextRowIndex as that row has been removed meanwhile
                                            nextRowIndex--;
                                        }
                                        this._selectCell(nextRowIndex, cellIndex, cellOptions);
                                    } else {
                                        // we were in the last group, so go back to the top
                                        this._selectCell(borderRowIndex, cellIndex, cellOptions);
                                    }
                                },
                            });
                            return;
                        }
                    } else {
                        // there is no 'Add a line' row (i.e. the create feature is disabled), or the
                        // list is editable="top", we focus the first record of the next group if any,
                        // or we go back to the top of the list
                        nextRowIndex = $nextRow.length ?
                            ($nextRow.prop('rowIndex') - 2) :
                            borderRowIndex;
                    }
                }

                // if there is a (record) row to select, select it, otherwise, add a new record (in the
                // correct group, if the view is grouped)
                if (nextRowIndex !== null) {
                    // cellOptions.force = true;
                    this._selectCell(nextRowIndex, cellIndex, cellOptions);
                } else if (this.editable) {
                    // if for some reason (e.g. create feature is disabled) we can't add a new
                    // record, select the first record row
                    this.unselectRow().then(this.trigger_up.bind(this, 'add_record', {
                        groupId: groupId,
                        onFail: this._selectCell.bind(this, borderRowIndex, cellIndex, cellOptions),
                    }));
                }
            });
        },

        _onCellClick: function(event) {
            // The special_click property explicitely allow events to bubble all
            // the way up to bootstrap's level rather than being stopped earlier.
            var $td = $(event.currentTarget);
            var $tr = $td.parent();
            var rowIndex = $tr.prop('rowIndex') - 2;
            if (!this._isRecordEditable($tr.data('id')) || $(event.target).prop('special_click')) {
                return;
            }
            var fieldIndex = Math.max($tr.find('.o_field_cell').index($td), 0);
            this._selectCell(rowIndex, fieldIndex, {
                event: event
            });
        },

        _renderHeaderCellSearch: function(node) {
            var search_tr = $($('tr')[1]).find('input.input_text')
            var old_domain = JSON.parse(localStorage.getItem('domainlist'))
            var input_dict = {}
            var self = this;
            for (var i = 0; i < search_tr.length; i++) {
                var field = $(search_tr[i]).attr('name')
                var value = $(search_tr[i]).val()
                input_dict[String(field)] = value
            }
            const {
                icon,
                name,
                string,
                widget,
            } = node.attrs;
            var searched_value = _.filter(old_domain, function(domain) {
                return domain[0] == name;
            });
            var widget_list = ["monetary","date","many2one_avatar_user","badge","task_with_hours","timesheet_uom"];
            var value_of_tr = searched_value.length > 0 ? searched_value[0][2] : ""
            var value_of_tr1 = searched_value.length > 1 ? (searched_value[0][2]).split(' ')[0] +'/'+ (searched_value[1][2]).split(' ')[0] : ""
            var order = this.state.orderedBy;
            var isNodeSorted = order[0] && order[0].name === name;
            var field = this.state.fields[name];
            var $td = $('<td>', {
                class: 'search_td'
            });
            if (name) {
                $td.attr('data-name', name);
            } else if (string) {
                $td.attr('data-string', string);
            }
            if (!field) {
                return $td;
            }
            var description = string || field.string;
            if (!widget || widget_list.includes(widget)) {
                if (string !== " " && field.store) {
                    if (field.type == 'char') {
                        var search_div = $('<div>').attr({
                            'class': 'search_div'
                        });
                        var $input = $('<input>').attr({
                            type: 'text',
                            name: name,
                            data_name: name,
                            data_text: string,
                            val: input_dict[name],
                            placeholder: description,
                            autocomplete: "autocomplete",
                            'class': 'input_text'
                        });
                        var search_button = $('<button>').attr({
                            type: 'button',
                            name: name,
                            'class': 'search_button  fa fa-search',
                        });
                        var remove_button = $('<button>').attr({
                            type: 'button',
                            name: name,
                            'class': 'remove_button  fa fa-remove hidden_button',
                        });
                        $input.text(description)
                        $input.val(value_of_tr)
                        if (value_of_tr) {
                            $(search_button).addClass('hidden_button');
                            $(remove_button).removeClass('hidden_button');
                        }
                        if ($(search_button).hasClass('hidden_button')) {
                            $input.attr('readonly', 'readonly');
                            $input.css('background-color', '#dfdfdf');
                            $input.css('border-radius', '20px');
                        }
                        search_div.append($input)
                        search_div.append(remove_button)
                        search_div.append(search_button)
                        //					$td.append($input)
                        $td.append(search_div)
                    }
                    if (field.type == 'float') {
                        var search_div = $('<div>').attr({
                            'class': 'search_div'
                        });
                        var $input = $('<input>').attr({
                            type: 'number',
                            name: name,
                            data_name: name,
                            data_text: string,
                            placeholder: description,
                            autocomplete: "autocomplete",
                            'class': 'input_text'
                        });
                        var search_button = $('<button>').attr({
                            type: 'button',
                            name: name,
                            'class': 'search_button  fa fa-search'
                        });
                        var remove_button = $('<button>').attr({
                            type: 'button',
                            name: name,
                            'class': 'remove_button  fa fa-remove hidden_button',
                        });
                        $input.text(description)
                        $input.val(value_of_tr)
                        if (value_of_tr) {
                            $(search_button).addClass('hidden_button');
                            $(remove_button).removeClass('hidden_button');
                        }
                        if ($(search_button).hasClass('hidden_button')) {
                            $input.attr('readonly', 'readonly');
                            $input.css('background-color', '#dfdfdf');
                            $input.css('border-radius', '20px');
                        }
                        search_div.append($input)
                        search_div.append(remove_button)
                        search_div.append(search_button)
                        //					$td.append($input)
                        $td.append(search_div)
                    }
                    if (field.type == 'monetary') {
                        var search_div = $('<div>').attr({
                            'class': 'search_div'
                        });
                        var $input = $('<input>').attr({
                            type: 'text',
                            name: name,
                            data_name: name,
                            data_text: string,
                            placeholder: description,
                            autocomplete: "autocomplete",
                            'class': 'input_text'
                        });
                        var search_button = $('<button>').attr({
                            type: 'button',
                            name: name,
                            'class': 'search_button  fa fa-search'
                        });
                        var remove_button = $('<button>').attr({
                            type: 'button',
                            name: name,
                            'class': 'remove_button  fa fa-remove hidden_button',
                        });
                        $input.text(description)
                        $input.val(value_of_tr)
                        if (value_of_tr) {
                            $(search_button).addClass('hidden_button');
                            $(remove_button).removeClass('hidden_button');
                        }
                        if ($(search_button).hasClass('hidden_button')) {
                            $input.attr('readonly', 'readonly');
                            $input.css('background-color', '#dfdfdf');
                            $input.css('border-radius', '20px');
                        }
                        search_div.append($input)
                        search_div.append(remove_button)
                        search_div.append(search_button)
                        $td.append(search_div)
                    }
                    if (field.type == 'selection') {
                        var search_div = $('<div>').attr({
                            'class': 'search_div'
                        });
                        var $input = $('<input>').attr({
                            type: 'text',
                            name: name,
                            data_name: name,
                            data_text: string,
                            placeholder: description,
                            autocomplete: "autocomplete",
                            'class': 'input_text'
                        });
                        var search_button = $('<button>').attr({
                            type: 'button',
                            name: name,
                            'class': 'search_button  fa fa-search'
                        });
                        var remove_button = $('<button>').attr({
                            type: 'button',
                            name: name,
                            'class': 'remove_button  fa fa-remove hidden_button',
                        });
                        $input.text(description)
                        $input.val(value_of_tr)
                        if (value_of_tr) {
                            $(search_button).addClass('hidden_button');
                            $(remove_button).removeClass('hidden_button');
                        }
                        if ($(search_button).hasClass('hidden_button')) {
                            $input.attr('readonly', 'readonly');
                            $input.css('background-color', '#dfdfdf');
                            $input.css('border-radius', '20px');
                        }
                        search_div.append($input)
                        search_div.append(remove_button)
                        search_div.append(search_button)
                        $td.append(search_div)
                    }
                    if (field.type == 'integer') {
                        var search_div = $('<div>').attr({
                            'class': 'search_div'
                        });
                        var $input = $('<input>').attr({
                            type: 'number',
                            name: name,
                            data_name: name,
                            data_text: string,
                            placeholder: description,
                            autocomplete: "autocomplete",
                            'class': 'input_text'
                        });
                        var search_button = $('<button>').attr({
                            type: 'button',
                            name: name,
                            'class': 'search_button  fa fa-search '
                        });
                        var remove_button = $('<button>').attr({
                            type: 'button',
                            name: name,
                            'class': 'remove_button  fa fa-remove hidden_button',
                        });
                        $input.text(description)
                        $input.val(value_of_tr)
                        if (value_of_tr) {
                            $(search_button).addClass('hidden_button');
                            $(remove_button).removeClass('hidden_button');
                        }
                        if ($(search_button).hasClass('hidden_button')) {
                            $input.attr('readonly', 'readonly');
                            $input.css('background-color', '#dfdfdf');
                            $input.css('border-radius', '20px');
                        }
                        search_div.append($input)
                        search_div.append(remove_button)
                        search_div.append(search_button)
                        $td.append(search_div)
                    }

                    if (field.type == 'many2one') {
                        var search_div = $('<div>').attr({
                            'class': 'search_div'
                        });
                        var $input = $('<input>').attr({
                            type: 'text',
                            name: name,
                            data_name: name,
                            data_text: string,
                            placeholder: description,
                            autocomplete: "autocomplete",
                            'class': 'input_text'
                        });
                        var search_button = $('<button>').attr({
                            type: 'button',
                            name: name,
                            'class': 'search_button  fa fa-search'
                        });
                        var remove_button = $('<button>').attr({
                            type: 'button',
                            name: name,
                            'class': 'remove_button  fa fa-remove hidden_button',
                        });

                        $input.text(description)
                        $input.val(value_of_tr)
                        if (value_of_tr) {
                            $(search_button).addClass('hidden_button');
                            $(remove_button).removeClass('hidden_button');
                        }
                        if ($(search_button).hasClass('hidden_button')) {
                            $input.attr('readonly', 'readonly');
                            $input.css('background-color', '#dfdfdf');
                            $input.css('border-radius', '20px');
                        }
                        search_div.append($input)
                        search_div.append(remove_button)
                        search_div.append(search_button)
                        $td.append(search_div)
                    }
                    if (field.type == 'datetime' || field.type == 'date') {
                        var search_div = $('<div>').attr({
                            'class': 'search_div'
                        });
                        var $input_date1 = $('<input>').attr({
                            type: 'text',
                            name: name,
                            placeholder: 'Date Range',
                            autocomplete: "autocomplete",
                            width: '150px',
                            'class': 'input_text',
                            'style': 'min-width:200px !important'
                        });
                        var search_button = $('<button>').attr({
                            type: 'button',
                            name: name,
                            'class': 'search_button  fa fa-search'
                        });
                        var remove_button = $('<button>').attr({
                            type: 'button',
                            name: name,
                            'class': 'remove_button  fa fa-remove hidden_button',
                        });
                        $input_date1.daterangepicker({
                            autoUpdateInput: false,
                            locale: {
                                cancelLabel: 'Clear'
                            }
                        });
                        $input_date1.on('apply.daterangepicker', function(ev, picker) {
                            $input_date1.val(picker.startDate.format('MM/DD/YYYY') + '-' + picker.endDate.format('MM/DD/YYYY'));
                            var e = $.Event("keypress", {
                                which: 13
                            });
                            $input_date1.trigger(e);
                            e.keyCode = 13
                            self._onfilter(e)
                            $input_date1.change()
                        });

                        $input_date1.on('cancel.daterangepicker', function(ev, picker) {
                            $input_date1.val('');
                            var e = $.Event("keypress", {
                                which: 13
                            });
                            $input_date1.trigger(e);
                            e.keyCode = 13
                            self._onfilter(e)
                            $input_date1.change()
                        });
                        $input_date1.text(description)
                        $input_date1.val(value_of_tr1)



                        if (value_of_tr1) {
                            $(search_button).addClass('hidden_button');
                            $(remove_button).removeClass('hidden_button');
                        }
                        if ($(search_button).hasClass('hidden_button')) {
                            $input_date1.attr('readonly', 'readonly');
                            //                            $input_date1.css('min-width', '200px !important');
                            $input_date1.css('background-color', '#dfdfdf');
                            $input_date1.css('border-radius', '20px');
                        }
                        search_div.append($input_date1)
                        search_div.append(remove_button)
                        search_div.append(search_button)
                        $td.append(search_div)
                    }
                }
            }
            return $td;
        },

        _renderHeader: function() {
            var data = this._super.apply(this, arguments);
            var self = this
            var search_table = $('table')
            $('<table>').removeAttr('style')
            if (self.hasSelectors == true && self.isGrouped == false) {
                var $tr1 = $('<tr>').append(_.map(this.columns, self._renderHeaderCellSearch.bind(self)));
                if (self.hasSelectors) {
                    $tr1.prepend(self._renderSelector('td'));
                }
                var new_tr = data.append($tr1);
                $($(new_tr[0])[0].rows[1].cells[0]).css('display', 'table-column')
                return new_tr

            }
            return data;
        },
        _onKeyPress: function(ev) {
            ev.stopPropagation(); // to prevent jquery's blockUI to cancel event
        },

        _computeAggregates: function() {
            var self = this;
            if (self.aggre) {
                _.each(self.columns, self._computeColumnAggregates.bind(self, self.aggre));
            } else {
                this._super.apply(this, arguments);
            }

        },

        async _renderView() {
            if (this.state.count == 0) {
                this.state.count = 1
            }
            return this._super.apply(this,arguments)
        },

        _freezeColumnWidths: function () {
            var result = this._super();
            const table = this.el.getElementsByTagName('table')[0];
            if (table.style.tableLayout == 'fixed') {
                table.style.tableLayout = 'auto';
            }
            return result

        },

        _renderRows: function() {
            if (this.filter_data_trs && this.hasSelectors == true) {
                var filter = this.filter_data_trs
                var tr = this.state.data
                var list_return = []
                var list_aggregated = []
                for (var j = 0; j < filter.length; j++) {
                    for (var i = 0; i < tr.length; i++) {
                        if (filter[j].id == tr[i].data.id) {
                            list_return.push(tr[i])
                        }
                    }
                }
                this.aggre = list_return
                return list_return.map(this._renderRow.bind(this))
            } else {
                return this._super();
            }
        },

        _formatMomentToServer: function(momentValue) {
            return momentValue.locale('en').format(this.serverFormat);
        },

        _onSearch: function(event) {
            var self = this
            var field_name = $(event.currentTarget).attr('name')
            let all_input_tags = $($('tr')[1]).find('input.input_text')
            if (!all_input_tags.length) {
                all_input_tags = $($('tr')[5]).find('input.input_text')
            }
            var search_tr = all_input_tags.filter(function(el) {
                if (all_input_tags[el].name == field_name) {
                    var e = $.Event("keypress", {
                        which: 13
                    });
                    $(all_input_tags[el]).trigger(e);
                    e.keyCode = 13
                    self._onfilter(e)
                }
            });
        },

        _onRemove: function(event) {
            this.hasSelectors = false
            var self = this
            var updated_domain = []
            var old_domain = [];
            var field_name = $(event.currentTarget).attr('name')
            let all_input_tags = $($('tr')[1]).find('input.input_text')
            if (!all_input_tags.length) {
                all_input_tags = $($('tr')[5]).find('input.input_text')
            }
            var search_tr = all_input_tags.filter(function(el) {
                if (all_input_tags[el].name == field_name) {
                    all_input_tags[el].value = ''
                    var e = $.Event("keypress", {
                        which: 13
                    });
                    $(all_input_tags[el]).trigger(e);
                    e.keyCode = 13

                }
            });
            var prepare_domain = self.state.domain.filter(function(el) {
                if (field_name != el[0]) {
                    updated_domain.push(el)
                }
            });

            if (JSON.parse(localStorage.getItem('domainlist'))) {
                var prepare_old_domain = JSON.parse(localStorage.getItem('domainlist')).filter(function(el) {
                    if (field_name != el[0]) {
                        old_domain.push(el)
                    }
                });
                localStorage.setItem('domainlist', JSON.stringify(old_domain));
            };
            this.trigger_up("custom_update_advance_search_renderer", {
                customFieldName: field_name,
                updated_domain:updated_domain,
            });
            self.hasSelectors = true;
            self.customFieldName = field_name;
            this._renderHeader();
        },

        _onfilter: function(e) {
            if (e.key === 'Enter' || e.keyCode === 13) {
                var domain_list = []
                var self = this
                // this.state.domain.forEach(function(e) {
                //     domain_list.push(e)
                // })
                let all_input_tags = $($('tr')[1]).find('input.input_text')
                if (!all_input_tags.length) {
                        all_input_tags = $($('tr')[5]).find('input.input_text')
                    }
                var search_tr = all_input_tags.filter(function(el) {
                    return all_input_tags[el].value
                });
                if (search_tr.length == 0) {
                    self.perform_search(self, domain_list);
                }
                for (var i = 0; i < search_tr.length; i++) {
                    var field = $(search_tr[i]).attr('name')
                    var string = search_tr[i].textContent
                    var value = $(search_tr[i]).val()
                    if (value) {
                        if (domain_list.length) {
                            for (var k = 0; k < domain_list.length; k++) {
                                if (domain_list[k].includes(field)) {
                                    if (this.state.fields[field].type == "date") {
                                        var startDate = moment(_.str.strip(value.split('-')[0])).format("YYYY-MM-DD");
                                        var endDate = moment(_.str.strip(value.split('-')[1])).format("YYYY-MM-DD");
                                        if (startDate == 'Invalid date' || endDate == 'Invalid date') {
                                           window.alert("Please enter valid input for " + string);
                                        } else {
                                            if (domain_list[k][1] == ">=") {
                                                domain_list[k] = [field, '<=', endDate]
                                            } else {
                                                domain_list[k] = [field, '>=', startDate]
                                            }
                                        }
                                    } else if (this.state.fields[field].type == "datetime") {
                                        var startDate = moment(_.str.strip(value.split('-')[0])).format("YYYY-MM-DD HH:mm:ss");
                                        var endDate = moment(_.str.strip(value.split('-')[1])).format("YYYY-MM-DD 23:59:59");
                                        if (startDate == 'Invalid date' || endDate == 'Invalid date') {
                                           window.alert("Please enter valid input for " + string);
                                        } else {
                                            var d = new Date(startDate);
                                            var d1 = new Date(endDate);
                                            var date_value = d.getUTCFullYear() + '-' + (d.getUTCMonth() + 1) + '-' + d.getUTCDate() + ' ' + d.getUTCHours() + ':' + d.getUTCMinutes() + ':' + d.getUTCSeconds();
                                            var date_value1 = d1.getUTCFullYear() + '-' + (d1.getUTCMonth() + 1) + '-' + d1.getUTCDate() + ' ' + d1.getUTCHours() + ':' + d1.getUTCMinutes() + ':' + d1.getUTCSeconds();

                                            if (domain_list[k][1] == ">=") {
                                                domain_list[k] = [field, '<=', date_value1]
                                            } else {
                                                domain_list[k] = [field, '>=', date_value]
                                            }
                                        }
                                    } else if (this.state.fields[field].type == "monetary" || this.state.fields[field].type == "float" || this.state.fields[field].type == "integer") {
                                        domain_list[k] = [field, '=', value]
                                    } else {
                                        domain_list[k] = [field, 'ilike', value]
                                    }
                                } else {
                                    if (this.state.fields[field].type == "date") {
                                        var startDate = moment(_.str.strip(value.split('-')[0])).format("YYYY-MM-DD");
                                        var endDate = moment(_.str.strip(value.split('-')[1])).format("YYYY-MM-DD");
                                        if (startDate == 'Invalid date' || endDate == 'Invalid date') {
                                           window.alert("Please enter valid input for " + string);
                                        } else {
                                            domain_list.push([field, '<=', endDate])
                                            domain_list.push([field, '>=', startDate])
                                        }
                                    } else if (this.state.fields[field].type == "datetime") {
                                        var startDate = moment(_.str.strip(value.split('-')[0])).format("YYYY-MM-DD HH:mm:ss");
                                        var endDate = moment(_.str.strip(value.split('-')[1])).format("YYYY-MM-DD 23:59:59");
                                        if (startDate == 'Invalid date' || endDate == 'Invalid date') {
                                            window.alert("Please enter valid input for " + string);
                                        }  else {
                                            var d = time.str_to_datetime(startDate);
                                            var d = new Date(startDate);
                                            var d1 = new Date(endDate);
                                            var date_value = d.getUTCFullYear() + '-' + (d.getUTCMonth() + 1) + '-' + d.getUTCDate() + ' ' + d.getUTCHours() + ':' + d.getUTCMinutes() + ':' + d.getUTCSeconds();
                                            var date_value1 = d1.getUTCFullYear() + '-' + (d1.getUTCMonth() + 1) + '-' + d1.getUTCDate() + ' ' + d1.getUTCHours() + ':' + d1.getUTCMinutes() + ':' + d1.getUTCSeconds();
                                            domain_list.push([field, '<=', date_value1])
                                            domain_list.push([field, '>=', date_value])
                                        }

                                    } else if (this.state.fields[field].type == "monetary" || this.state.fields[field].type == "float" || this.state.fields[field].type == "integer") {
                                        domain_list.push([field, '=', parseFloat(value)])
                                    } else {
                                        domain_list.push([field, 'ilike', value])
                                    }
                                }
                            }
                        } else {
                            if (this.state.fields[field].type == "date") {
                                var startDate = moment(_.str.strip(value.split('-')[0])).format("YYYY-MM-DD");
                                var endDate = moment(_.str.strip(value.split('-')[1])).format("YYYY-MM-DD");
                                if (startDate == 'Invalid date' || endDate == 'Invalid date') {
                                    window.alert("Please enter valid input for " + string);
                                } else {
                                    domain_list.push([field, '<=', endDate])
                                    domain_list.push([field, '>=', startDate])
                                }
                            } else if (this.state.fields[field].type == "datetime") {
                                var startDate = moment(_.str.strip(value.split('-')[0])).format("YYYY-MM-DD HH:mm:ss");
                                var endDate = moment(_.str.strip(value.split('-')[1])).format("YYYY-MM-DD 23:59:59");
                                if (startDate == 'Invalid date' || endDate == 'Invalid date') {
                                    window.alert("Please enter valid input for " + string);
                                } else {
                                    var d = new Date(startDate);
                                    var d1 = new Date(endDate);
                                    var date_value = d.getUTCFullYear() + '-' + (d.getUTCMonth() + 1) + '-' + d.getUTCDate() + ' ' + d.getUTCHours() + ':' + d.getUTCMinutes() + ':' + d.getUTCSeconds();
                                    var date_value1 = d1.getUTCFullYear() + '-' + (d1.getUTCMonth() + 1) + '-' + d1.getUTCDate() + ' ' + d1.getUTCHours() + ':' + d1.getUTCMinutes() + ':' + d1.getUTCSeconds();
                                    domain_list.push([field, '<=', date_value1])
                                    domain_list.push([field, '>=', date_value])
                                }

                            } else if (this.state.fields[field].type == "monetary" || this.state.fields[field].type == "float" || this.state.fields[field].type == "integer") {
                                domain_list.push([field, '=', parseFloat(value)])
                            } else {
                                domain_list.push([field, 'ilike', value])
                            }
                        }
                    }


                }
                localStorage.setItem('domainlist', JSON.stringify(domain_list));
                self.perform_search(self, domain_list);
            }
        },

        perform_search: function(self, domain_list) {
             this.trigger_up("enter_update_advance_search_renderer", {
                    domain_list: domain_list,
                });

             self.hasSelectors = true;
        },
    })

    listCont.include({
            /**
         * Overrides to update the list of selected records
         *
         * @override
         */
        update: function (params, options) {
            var self = this;
            var prepare_old_domain = JSON.parse(localStorage.getItem('domainlist'))
            if (params.domain && params.domain != prepare_old_domain) {
                params['domain'] = params.domain.concat(prepare_old_domain);
            }

            if (!prepare_old_domain.length && !params.domain && self.renderer.state.domain) {
                localStorage.setItem('domainlist', JSON.stringify(self.renderer.state.domain));
            }

            return this._super.apply(this,arguments);
        },
    });

    return ListRendererCust;

});
