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

    location_view.js, Copyright 2019 Nathan Jones (Nathan@jones.one)
*/
function location_load() {
    $('#location_view').load('../partials/location_partial.html', function () {

        location_view_update();
        location_setup_modal();

    });
}

function location_view_update() {

    jQuery.get("/api/v1/location", function (locations) {

        let output = "";

        locations.location.forEach(function (location) {
            output += '<tr><td>' + location.location_id + '</td><td>' + location.location_label +
                '</td><td><button type="button" class="btn btn-primary" data-toggle="modal" ' +
                'data-target="#location_modal" data-purpose="Edit" ' +
                'data-location-id="' + location.location_id + '" ' +
                'data-location-label="' + location.location_label + '">Edit</button></td></tr>';
        });

        document.getElementById("location_table_body").innerHTML = output;
    });

}

function location_setup_modal() {
    $('#location_modal').on('show.bs.modal', function (event) {
        let button = $(event.relatedTarget); // Button that triggered the modal
        let purpose = button.data('purpose');
        let location_id = button.data('locationId'); // Extract info from data-* attributes
        let location_label = button.data('locationLabel');

        let modal = $(this);

        modal.find('.modal-title').text(purpose + ' Location');

        let modal_loc_id_form = modal.find('#location_id_form');
        let modal_loc_label_input = modal.find('#location_label');
        let modal_delete = modal.find('#location_delete');

        if (purpose === "Edit") {
            modal_delete.show();

            modal_loc_id_form.show();
            modal_loc_id_form.find('#location_id').val(location_id);

            modal_loc_label_input.val(location_label);

            modal.find('#location_submit').off('click').click(function () {
                location_update_location(location_id, modal_loc_label_input.val());
            });

            modal_delete.off('click').click( function() {
                location_delete_location(location_id);
            });

        } else {
            modal_delete.hide();

            modal_loc_id_form.hide();
            modal.find('#location_submit').off('click').click(function () {
                location_create_location(modal_loc_label_input.val());
            });
            modal_loc_label_input.val("");
        }

    })
}

function location_update_location(location_id, location_label) {
    $.ajax({
        url: '/api/v1/location/' + location_id,
        type: 'PUT',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({
            "location_label": location_label
        })
    }).always(function () {
        location_view_update();
    });
}

function location_create_location(location_label) {
    $.ajax({
        url: '/api/v1/location',
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({
            "location_label": location_label
        })
    }).always(function () {
        location_view_update();
    });
}

function location_delete_location(location_id) {
    $.ajax({
        url: '/api/v1/location/' + location_id,
        type: 'DELETE',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({})
    }).always(function () {
        location_view_update();
    });
}