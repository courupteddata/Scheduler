/*
    This file is part of Scheduler.

    Scheduler is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Scheduler is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Scheduler.  If not, see <https://www.gnu.org/licenses/>.

    stats_view.js, Copyright 2019 Nathan Jones (Nathan@jones.one)
*/
let stats_selected_id = "";
let stats_start_window = "";
let stats_end_window = "";

function stats_load() {
    $('#stats_view').load('../partials/stats_partial.html', function () {

        stats_populate_employee_list();
        stats_handle_employee_change();
        stats_handle_window_change();
        stats_handle_refresh_click();
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
        stats_update_table();
    });
}

function stats_handle_refresh_click(){
    $("#stats_refresh_employee_select").on('click', function(){
        stats_populate_employee_list();
    });
}

function stats_handle_window_change() {
    $("#stats_window_start").change(function (e) {
        if (e.target.value !== "") {
            stats_start_window = new Date(e.target.value).toISOString()
        } else {
            stats_start_window = "";
        }
        stats_update_table();
    });
    $("#stats_window_end").on('change', function (e) {
        if (e.target.value !== "") {
            stats_end_window = new Date(e.target.value).toISOString()
        } else {
            stats_end_window = "";
        }
        stats_update_table();
    });
}

function stats_update_table() {
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

