let shift_start_window = "";
let shift_end_window = "";
let shift_selected_employee_id = [];
let shift_selected_location_id = [];

function shift_load() {
    $('#shift_view').load('../partials/shift_partial.html', function () {


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