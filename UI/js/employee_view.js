let employee_requirement_types = [];

let employee_original_location_ids = new Set();
let employee_updated_location_ids = new Set();

let employee_requirements_to_add = {};

let employee_delete_requirement_ids = new Set();

let employee_name_change = false;
let employee_updated_name = "";

function employee_load() {

    $('#employee_view').load('../partials/employee_partial.html', function () {

        employee_update_table();
        employee_setup_modal();
    });
}

function employee_update_table() {

    jQuery.get("/api/v1/entity", function (data) {

        let output = "";
        data.entity.forEach(function (employee) {
            output +=
                '<tr><td>' + employee.entity_id +
                '</td><td>' + employee.entity_name +
                '</td><td><button class="btn btn-primary" data-toggle="modal" data-target="#employee_modal" data-purpose="Edit" ' +
                'data-entity-id="' + employee.entity_id + '" data-entity-name="' + employee.entity_name + '" >Edit</button></td></tr>';
        });

        document.getElementById("employee_table_body").innerHTML = output;
    });
}

function employee_setup_modal() {
    let employee_modal = $('#employee_modal');

    employee_modal.on('show.bs.modal', function (event) {
        let button = $(event.relatedTarget); // Button that triggered the modal
        let purpose = button.data('purpose');
        let entity_id = button.data('entityId'); // Extract info from data-* attributes
        let entity_name = button.data("entityName");

        let modal = $(this);

        modal.find('#employee_modal_label').text(purpose + ' Employee');

        let modal_entity_id_form = modal.find('#employee_id_field');
        let modal_entity_name_input = modal.find('#employee_name_field');

        let modal_submit = modal.find("#employee_submit");
        let modal_delete = modal.find('#employee_delete');

        let modal_requirement_type_select = modal.find("#employee_requirement_type_select");

        let modal_requirement_view = modal.find("#employee_requirement_partial");


        modal_requirement_type_select.off("changed.bs.select").selectpicker('refresh').on('changed.bs.select', function (e) {
            stats_selected_id = $(e.currentTarget).val();
            modal_requirement_view.empty().load(requirement_types[stats_selected_id].partial);
        });


        if (purpose === "Edit") {
            modal_delete.show();

            modal_entity_id_form.show();
            modal_entity_id_form.find('#employee_id_input').val(entity_id);

            modal_entity_name_input.val(entity_name);

            modal_submit.off('click').click(function () {
                //location_update_location(location_id, modal_loc_label_input.val());
            });

            modal_delete.off('click').click(function () {
                //location_delete_location(location_id);
            });

        } else {
            modal_delete.hide();

            modal_entity_id_form.hide();
            modal.find('#employee_submit').off('click').click(function () {
                //location_create_location(modal_loc_label_input.val());
            });
            //modal_loc_label_input.val("");
        }


    });

    employee_modal.on('hide.bs.modal', function () {
        let modal = $(this);
        modal.find("#employee_requirement_partial").empty();

        modal.find("#employee_requirement_type_select").val('').selectpicker('refresh');
    });
}

function employee_fill_location_modal(entity_id, select_element) {
    jQuery.get("/api/v1/location", function (locations) {


        jQuery.get("/api/v1/entity" + entity_id + "/location", function (locations) {

        });


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
