let shift_start_window = "";
let shift_end_window = "";

let shift_view_partial = "";
let shift_list_of_shifts = [];

let shift_calendar = undefined;

function shift_load() {
    $('#shift_view').load('../partials/shift_partial.html', function () {
        shift_view_partial = $(this);
        shift_refresh_select();
        shift_setup_button_clicks_and_change_handlers();
        shift_create_calendar();
        shift_update_events_list();
    });
}


function shift_delete_shift(shift_id, success_callback) {
    $.ajax({
        url: '/api/v1/shift/' + shift_id,
        type: 'DELETE'
    }).done(function () {
        success_callback();
    });
}

function shift_update_shift(shift_id, data, success_callback) {
    $.ajax({
        url: '/api/v1/shift/' + shift_id,
        type: 'PUT',
        data: JSON.stringify(data)
    }).done(function () {
        success_callback();
    });
}

function shift_create_shift(data, success_callback) {
    $.ajax({
        url: '/api/v1/shift',
        type: 'POST',
        data: JSON.stringify(data)
    }).done(function () {
        success_callback();
    });
}

function shift_create_template_shift(data, success_callback) {
    $.ajax({
        url: '/api/v1/shift/template',
        type: 'POST',
        data: JSON.stringify(data)
    }).done(function () {
        success_callback();
    });

}

function shift_get_shifts(success_callback) {
    $.ajax({
        url: '/api/v1/shift?' + shift_get_query_string(),
        type: 'GET'
    }).done(function (data) {
        success_callback(data.shift);
    });
}

function shift_create_calendar() {

    shift_calendar = new FullCalendar.Calendar(document.getElementById("shift_calendar_view"), {
            plugins: ['dayGrid', 'interaction'],
            defaultView: 'dayGridMonth',
            editable: true,
            currentTimezone: 'local',
            /**
             eventDrop: function (info) {
            if (!confirm("Are you sure you want to move this shift to " + info.event.start.toLocaleString() + "?")) {
                info.revert();
            } else {
                var employee_id;
                $.ajax({
                    url: 'http://127.0.0.1:5000/api/v1/entity',
                    type: 'GET',
                    success: function (employees) {
                        employees.entity.forEach(function (employee) {
                            if (info.event.title == employee.entity_name) {
                                employee_id = employee.entity_id
                            }
                        });
                        $.ajax({
                            url: 'http://127.0.0.1:5000/api/v1/shift/' + info.event.id,
                            type: 'DELETE',
                            success: function (data) {
                                $.ajax({
                                    url: 'http://127.0.0.1:5000/api/v1/shift',
                                    type: 'POST',
                                    contentType: 'application/json;charset=UTF-8',
                                    data: JSON.stringify({
                                        "start": info.event.start,
                                        "end": info.event.end,
                                        "location_id": window.location.search.match(/id=[^&])[0].substr(3),
                                        "entity_id": employee_id
                                    })
                                });
                            }
                        });
                    }
                });
            }
        },
             eventClick: function (info) {
            var tzoffset = (new Date()).getTimezoneOffset() * 60000; //offset in milliseconds
            var start = (new Date(info.event.start - tzoffset)).toISOString().slice(0, 19)
            var end = (new Date(info.event.end - tzoffset)).toISOString().slice(0, 19)
            $('#start_time')[0].value = start;
            $('#end_time')[0].value = end;
            jQuery.get("http://127.0.0.1:5000/api/v1/entity", function (data) {
                data.entity.forEach(function (employee) {
                    opt = document.createElement('option');
                    opt.appendChild(document.createTextNode(employee.entity_name));
                    opt.value = employee.entity_id;
                    document.getElementById("employee").appendChild(opt);
                });
            });
            $('#shift_id')[0].value = info.event.id;
            $('#submit')[0].setAttribute('onclick', 'submitEdit(this.form);');
            $('#delete')[0].removeAttribute('hidden');
            $('.modal-title')[0].innerHTML = 'Edit Shift'
            $('.modal').modal();
        },*/
            dateClick: function (info) {
                shift_prepare_modal("Add", info);
            },
            header: {
                left: '',
                center: 'title prev,today,next',
                right: ''
            },
            events: []
        }
    );
    shift_calendar.render();

//calendar.render();
}

function shift_setup_button_clicks_and_change_handlers() {
    shift_view_partial.find("#shift_refresh_selects").off('click').on('click', function () {
        shift_refresh_select();
    });

    shift_view_partial.find("#shift_window_start").on('change', function (e) {
        if (e.target.value !== "") {
            shift_start_window = new Date(e.target.value).toISOString()
        } else {
            shift_start_window = "";
        }
    });
    shift_view_partial.find("#shift_window_end").on('change', function (e) {
        if (e.target.value !== "") {
            shift_end_window = new Date(e.target.value).toISOString()
        } else {
            shift_end_window = "";
        }
    });

    shift_view_partial.find("#shift_export_button").off('click').on('click', function (e) {
        e.preventDefault();
        window.location.href = ('/api/v1/shift?export=true&' + shift_get_query_string());
    });

    shift_view_partial.find("#shift_update_button").off('click').on('click', function () {
        shift_update_events_list();
    });
}

function shift_refresh_select() {
    shift_fill_location_select(shift_view_partial.find("#shift_location_select"));
    shift_fill_employee_list(shift_view_partial.find("#shift_employee_select"));

}

function shift_fill_location_select(select_element) {
    jQuery.get("/api/v1/location", function (locations) {

        let output = '<optgroup label="Special"><option value="-1">All Locations</option></optgroup>';
        locations.location.forEach(function (location) {
            output += '<option value="' + location.location_id + '">' + location.location_label + '</option>'
        });

        select_element.append(output).selectpicker('refresh');
    });
}

function shift_fill_employee_list(select_element) {

    jQuery.get("/api/v1/entity", function (entities) {

        let output = '<optgroup label="Special"><option value="-2">All</option><option value="-1">Empty Shifts</option></optgroup>';

        entities.entity.forEach(function (entity) {
            output += '<option data-tokens="' + entity.entity_name + '" value="' + entity.entity_id + '">' + entity.entity_name + '</option>';
        });

        select_element.empty().append(output).selectpicker('refresh');


    });
}

function shift_get_query_string() {
    let employee_values = new Set(shift_view_partial.find("#shift_employee_select").val());
    let location_values = new Set(shift_view_partial.find("#shift_location_select").val());

    let query_parts = [];

    if (!employee_values.has("-2")) {
        //If all isn't selected then create the query params
        for (let item of employee_values) {
            query_parts.push("entity_id=" + item);
        }
    }

    if (!location_values.has(-1)) {
        //If not all locations
        for (let item of location_values) {
            query_parts.push("location_id=" + item);
        }
    }

    if (shift_start_window !== "") {
        query_parts.push("start=" + shift_start_window);
    }
    if (shift_end_window !== "") {
        query_parts.push("end=" + shift_end_window);
    }

    return query_parts.join("&");
}

function shift_update_events_list() {
    let entity_id_to_name = {};
    let location_id_to_label = {};

    $.when($.ajax({
        url: '/api/v1/entity',
        type: 'GET'
    }), $.ajax({
        url: '/api/v1/location',
        type: 'GET'
    }), $.ajax({
        url: '/api/v1/shift?' + shift_get_query_string(),
        type: 'GET'
    })).done(function (entity_list, location_list, shift_list) {

        entity_list[0].entity.forEach(function (item) {
            entity_id_to_name[item.entity_id] = item.entity_name;
        });
        location_list[0].location.forEach(function (item) {
            location_id_to_label[item.location_id] = item.location_label;
        });

        let event = [];

        shift_list[0].shift.forEach(function (item) {
            event.push({
                "start": item.start,
                "end": item.end,
                "id": item.shift_id,
                "title": item.entity_id == "-1" ? "Unassigned" : entity_id_to_name[item.entity_id],
                "extendedProps": {
                    "entity_id": item.entity_id,
                    "location_id": item.location_id,
                    "info": item.info
                }
            });
        });

        shift_calendar.removeAllEvents();
        shift_calendar.addEventSource(event);
    });
}

function shift_prepare_modal(purpose, info) {
    let shift_modal = $('#shift_modal', shift_view_partial);

    shift_modal.off('show.bs.modal').on('show.bs.modal', function () {
        let modal = $(this);

        //ID and Nome field
        let modal_shift_id_group = modal.find("#shift_modal_id_group");
        let modal_shift_id_input = modal.find("#shift_modal_shift_id");

        let modal_shift_location_select = modal.find("#shift_modal_location_select");
        let modal_shift_employee_select = modal.find("#shift_modal_employee_select");

        let modal_shift_start_datetime = modal.find("#shift_modal_start_datetime");
        let modal_shift_end_datetime = modal.find("#shift_modal_end_datetime");

        let modal_shift_info_input = modal.find("#shift_info_input");
        let modal_shift_repeat_till = modal.find("#shift_modal_repeat_until");

        modal.find("#shift_modal_label").text(purpose + " Shift");

        //Two Buttons
        let modal_submit = modal.find("#shift_submit");
        let modal_delete = modal.find('#shift_delete');

        //Clear the data
        modal_shift_employee_select.empty().selectpicker('render');


        if (purpose === "Edit") {
            let event = info.event;

            let modal_shift_info = event.extendedProps.info;
            let modal_shift_id = event.id;
            let modal_shift_location_id = event.extendedProps.location_id;
            let modal_shift_entity_id = event.extendedProps.entity_id;

            modal_delete.show();

            shift_fill_modal_location_select(modal_shift_location_select, function () {
                shift_fill_modal_employee_select(modal_shift_employee_select, modal_shift_location_select, function () {
                    modal_shift_employee_select.val(modal_shift_entity_id);
                });
            }, function () {
                modal_shift_location_select.val(modal_shift_location_id);
            });

            modal_shift_start_datetime.datetimepicker({"date": moment(event.start)});
            modal_shift_end_datetime.datetimepicker({"date": moment(event.end)});

            modal_shift_info_input.text(modal_shift_info);

            modal_shift_id_group.show();
            modal_shift_id_input.val(modal_shift_id);

            modal_submit.off('click').click(function () {
                let selected_locations = new Set(modal_shift_location_select.val());
                let selected_employee = modal_shift_employee_select.val();
                let selected_repeat_until = modal_shift_repeat_till.val();
                let info_text = modal_shift_info_input.text();
                shift_handle_submit(modal_shift_id, selected_locations, selected_employee, selected_repeat_until, info_text,
                    (new Date(modal_shift_start_datetime.val())).toISOString(), (new Date(modal_shift_end_datetime.val())).toISOString());

            });

            modal_delete.off('click').click(function () {
                shift_delete_shift(modal_shift_id, function () {
                    shift_calendar.removeEvent(modal_shift_id);
                });
            });

        } else {
            modal_delete.hide();
            modal_shift_id_group.hide();

            modal_shift_start_datetime.datetimepicker({"date": moment(info.dateStr + "T07:00")});
            modal_shift_end_datetime.datetimepicker({"date": moment(info.dateStr + "T15:00")});

            shift_fill_modal_location_select(modal_shift_location_select, function () {
                shift_fill_modal_employee_select(modal_shift_employee_select, modal_shift_location_select);
            });


            modal_submit.off('click').click(function () {
                let selected_locations = new Set(modal_shift_location_select.val());
                let selected_employee = modal_shift_employee_select.val();
                let selected_repeat_until = modal_shift_repeat_till.val();
                let info_text = modal_shift_info_input.text();


                shift_handle_submit(-1, selected_locations, selected_employee, selected_repeat_until, info_text,
                    (new Date(modal_shift_start_datetime.val())).toISOString(), (new Date(modal_shift_end_datetime.val())).toISOString());

            });
        }
    });

    shift_modal.modal();
}

function shift_fill_modal_location_select(select_element, success_onchange_callback, success_callback) {
    jQuery.get("/api/v1/location", function (locations) {
        let output = "";
        locations.location.forEach(function (location) {
            output += '<option value="' + location.location_id + '">' + location.location_label + '</option>'
        });

        select_element.off("changed.bs.select").on('changed.bs.select', success_onchange_callback);
        select_element.empty().append(output).val('').selectpicker('render').selectpicker('refresh');


        if (success_callback !== undefined) {
            success_callback();
        }
    });
}

function shift_fill_modal_employee_select(select_element, location_select, success_callback) {

    if (location_select.val().length === 1) {
        jQuery.get("/api/v1/location/" + location_select.val() + "/entity", function (entity_id) {

                let queries = [];

                entity_id.entity_ids.forEach(function (an_id) {
                    queries.push(jQuery.get("/api/v1/entity/" + an_id));
                });


                $.when.apply($, queries).then(function () {

                    let output = '<optgroup label="Special"><option value="-1">Empty</option></optgroup>';

                    for (let data of arguments) {
                        let element = data[0];

                        output += '<option data-tokens="' + element.entity_name + '" value="' + element.entity_id + '">' + element.entity_name + '</option>';
                    }


                    select_element.empty().append(output).selectpicker('refresh');

                    if (success_callback !== undefined) {

                        success_callback();
                    }


                });
            }
        );

    } else {
        //Too many employee were picked or none have been picked
        select_element.empty().append('<optgroup label="Special"><option value="-1">Empty</option></optgroup>').selectpicker('refresh');

        if (success_callback !== undefined) {

            success_callback();
        }
    }
}

function shift_handle_submit(shift_id, selected_locations, selected_employee, selected_repeat_until, info_text, shift_start, shift_end) {
    if (shift_id !== "" && shift_id !== -1) {
        shift_delete_shift(shift_id);
    }

    let data = {
        "info": info_text,
        "start": shift_start,
        "end": shift_end
    };

    let repeat_flag = false;

    if (('' + selected_employee) !== "-1" && '' + selected_employee !== "") {
        data["entity_id"] = selected_employee;
    } else {
        data["entity_id"] = -1;
    }

    if (selected_repeat_until !== "") {
        repeat_flag = true;
    }

    let requests = [];

    for (let location of selected_locations) {
        data["location_id"] = location;

        if (repeat_flag) {
            let item = {"end": selected_repeat_until, "sample": [data]};

            requests.push($.ajax({
                url: '/api/v1/shift/template',
                type: 'POST',
                contentType: 'application/json;charset=UTF-8',
                data: JSON.stringify(item)
            }));
        } else {
            requests.push($.ajax({
                url: '/api/v1/shift',
                type: 'POST',
                contentType: 'application/json;charset=UTF-8',
                data: JSON.stringify(data)
            }));
        }
    }
    $.when.apply($, requests).then(function () {
        shift_update_events_list();
    });
}