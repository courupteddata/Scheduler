let work_view_partial = undefined;

function work_load() {
    $('#work_view').load('../partials/work_partial.html', function () {
        work_view_partial = $(this);

        work_refresh_table();
        work_setup_button_clicks();
    });
}

function work_refresh_table() {
    jQuery.get("/api/v1/work", function (work) {

        let output = '';

        work.work.forEach(function (entry) {
            output += '<tr><td>' + entry.work_id +
                '</td><td>' + entry.work_progress +
                '</td><td>' + entry.work_message +
                '</td><td><button class="btn btn-secondary" data-work-id="' + entry.work_id +
                '">&times;</button></td></tr>';
        });

        let table_body = work_view_partial.find("#work_table_body");
        table_body.empty().append(output);
        $(":button", table_body).off("click").on("click", function (event) {
            let button = $(event.target);

            let work_id = button.data("workId");

            work_delete_entry(work_id, function () {
                work_refresh_table();
            })
        });
    });
}

function work_setup_button_clicks() {

    work_view_partial.find("#work_refresh").on("click", function () {
        work_refresh_table();
    });

    work_view_partial.find("#work_fill_schedule_button").on("click", function () {
        $.ajax({
            url: '/api/v1/scheduler/fill',
            type: 'POST'
        }).done(function () {
            work_refresh_table();
        });
    })

}

function work_delete_entry(work_id, success_callback) {
    $.ajax({
        url: '/api/v1/work/' + work_id,
        type: 'DELETE'
    }).done(success_callback);
}



