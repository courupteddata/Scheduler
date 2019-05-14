let stats_selected_id = "";
let stats_start_window = "";
let stats_end_window = "";

function stats_load() {
    $('#stats_view').load('../partials/stats_partial.html', function () {

        stats_populate_employee_list();
        stats_handle_employee_change();
        stats_handle_window_change();
    });

}

function stats_populate_employee_list() {

    jQuery.get("/api/v1/entity", function (entities) {

        let output = "";

        entities.entity.forEach(function (entity) {
            output += '<option data-tokens="' + entity.entity_name + '" value="' + entity.entity_id + '">' + entity.entity_name + '</option>';
        });

        $("#stats_employee_select").empty().append(output).selectpicker('refresh');


    });
}

function stats_handle_employee_change() {
    $("#stats_employee_select").on('changed.bs.select', function (e) {
        stats_selected_id = $(e.currentTarget).val();
        update_table();
    });
}

function stats_handle_window_change() {
    $("#stats_window_start").change(function (e) {
        if (e.target.value !== "") {
            stats_start_window = new Date(e.target.value).toISOString()
        } else {
            stats_start_window = "";
        }
        update_table();
    });
    $("#stats_window_end").on('change', function (e) {
        if (e.target.value !== "") {
            stats_end_window = new Date(e.target.value).toISOString()
        } else {
            stats_end_window = "";
        }
        update_table();
    });
}

function update_table() {
    let query = "";
    let previous = false;

    if (stats_start_window !== "") {
        query += "start=" + stats_start_window;
        previous = true;
    }

    if (stats_end_window !== "") {
        if (previous === true) {
            query += "&";
        }
        query += "end=" + stats_end_window;
    }

    if (query !== "") {
        query = "?" + query;
    }

    if (stats_selected_id === "") {
        return;
    }

    jQuery.get("/api/v1/entity/" + stats_selected_id + "/location", function (locations) {
        let labels = locations.location.reduce(function (map, obj) {
            map[obj.location_id] = obj.location_label;
            return map;
        }, {});

        jQuery.get("api/v1/entity/" + stats_selected_id + "/stats" + query, function (stats) {

            let output = "";

            stats.stats.forEach(function (location) {
                output += '<tr class="table"><td>' + location.location_id + '</td><td>' + labels[location.location_id] + '</td><td>' + location.shift_count + '</td><td>' + location.total_hours + '</td></tr>';
            });

            document.getElementById("stats_table_body").innerHTML = output;
        });
    });
}

