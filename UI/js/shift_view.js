let shift_start_window = "";
let shift_end_window = "";

let shift_view_partial = "";

function shift_load() {
    $('#shift_view').load('../partials/shift_partial.html', function () {
        shift_view_partial = $(this);
        shift_refresh_select();
        shift_setup_button_clicks();
    });
}


function shift_get_shifts(success_callback) {


    $.ajax({
        url: '/api/v1/shift',
        type: 'GET'
    })
        .done(function (data) {
            success_callback(data.shift);
        });
}

function shift_setup_button_clicks() {
    shift_view_partial.find("#shift_refresh_selects").off('click').on('click', function () {
        shift_refresh_select();
    });

    shift_view_partial.find("#shift_window_start").on('change', function (e) {
        if (e.target.value !== "") {
            shift_start_window = new Date(e.target.value).toISOString()
        } else {
            shift_start_window = "";
        }
        update_table();
    });
    shift_view_partial.find("#shift_window_end").on('change', function (e) {
        if (e.target.value !== "") {
            shift_end_window = new Date(e.target.value).toISOString()
        } else {
            shift_end_window = "";
        }
        update_table();
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


}