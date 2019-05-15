const employee_REQUIREMENT_TEMP = "TEMP"; //Only stored locally
const employee_REQUIREMENT_SERVER = "SERVER"; //From the database, unchanged
const employee_REQUIREMENT_DELETE = "DELETE"; //Marked for deletion

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

        //Reset the view
        modal.find("#employee_requirement_partial").empty();
        modal.find("#employee_requirement_type_select").val('').selectpicker('refresh');

        //
        let modal_employee_original_location_set = new Set();

        //ID and Nome field
        let modal_entity_id_form = modal.find('#employee_id_field');
        let modal_entity_name_input = modal.find('#employee_name_field');

        //Two Buttons
        let modal_submit = modal.find("#employee_submit");
        let modal_delete = modal.find('#employee_delete');


        //Location section
        let modal_location_select = modal.find("#employee_location_select");
        employee_fill_location_modal(entity_id, modal_location_select, modal_employee_original_location_set);

        //Requirement section
        let modal_requirement_type_select = modal.find("#employee_requirement_type_select");
        let modal_requirement_view = modal.find("#employee_requirement_partial");

        let modal_requirement_table = modal.find("#employee_requirement_table_body");
        let modal_requirement_list = [];

        //Update title of the modal depending on the purpose
        modal.find('#employee_modal_label').text(purpose + ' Employee');


        //Basic requirement select functionality
        modal_requirement_type_select.off("changed.bs.select").selectpicker('refresh').on('changed.bs.select', function (e) {
            let modal_requirement_selected_id = $(e.currentTarget).val();
            requirement_load_partial(modal_requirement_view, modal_requirement_selected_id,
                function () {
                    let temp = requirement_get_submit_data(modal_requirement_selected_id, modal_requirement_view);
                    temp["state"] = employee_REQUIREMENT_TEMP;
                    modal_requirement_list.push(temp);
                },
                function () {
                    modal_requirement_type_select.val('').selectpicker('refresh');
                    modal_requirement_view.empty();
                })
        });


        if (purpose === "Edit") {
            modal_delete.show();

            requirement_get_requirements(entity_id, function (data) {
                data.forEach(function (item) {
                    modal_requirement_list.push(item);
                });
                employee_refresh_requirements_list(modal_requirement_table, modal_requirement_list, function (event) {
                    let edit_button = $(event.relatedTarget);
                    let data_index = edit_button.data("requirementIndex");
                    let data = modal_requirement_list[data_index];

                    requirement_load_partial_with_data(modal_requirement_view, data ,
                        function () {
                            let temp = requirement_get_submit_data(requirement_get_type_number(data), modal_requirement_view);

                            if(data["state"] === employee_REQUIREMENT_SERVER ) {
                                modal_requirement_list[data_index]["state"] = employee_REQUIREMENT_DELETE;
                            }
                            temp["state"] = employee_REQUIREMENT_TEMP;
                            modal_requirement_list.push(temp);
                            modal_requirement_view.empty();
                        },
                        function () {
                            modal_requirement_type_select.val('').selectpicker('refresh');
                            modal_requirement_view.empty()
                        }, function () {

                            modal_requirement_view.empty();
                        })
                });
            });

            //Show employee id
            modal_entity_id_form.show();
            modal_entity_id_form.find('#employee_id_input').val(entity_id);

            //Update name
            modal_entity_name_input.val(entity_name);

            modal_submit.off('click').click(function () {
                let selected_values = new Set(modal_location_select.val());
                let new_name = modal_entity_name_input.val();

                if (new_name !== entity_name) {
                    employee_update_name(entity_id, new_name);
                }

                employee_update_location(entity_id, selected_values, modal_employee_original_location_set)
            });

            modal_delete.off('click').click(function () {
                employee_delete_one(entity_id);
            });

        } else {
            modal_delete.hide();

            modal_entity_id_form.hide();
            modal.find('#employee_submit').off('click').click(function () {
                let selected_values = new Set(modal_location_select.val());

                employee_create_one(modal_entity_name_input.val(), function (created_id) {
                    employee_update_location(created_id, selected_values, modal_employee_original_location_set)
                });
                //location_create_location(modal_loc_label_input.val());
            });
            //modal_loc_label_input.val("");
        }


    });
}

function employee_fill_location_modal(entity_id, select_element, original_location_ids) {
    select_element.empty();

    jQuery.get("/api/v1/location", function (locations) {
        let output = "";
        locations.location.forEach(function (location) {
            output += '<option value="' + location.location_id + '">' + location.location_label + '</option>'
        });

        select_element.append(output).selectpicker('refresh');


        jQuery.get("/api/v1/entity/" + entity_id + "/location", function (locations) {
            locations.location.forEach(function (location) {
                original_location_ids.add('' + location.location_id)
            });
            select_element.selectpicker('val', Array.from(original_location_ids));
        });

    });

}

function employee_create_one(name, success_callback) {
    $.ajax({
        url: '/api/v1/entity',
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({"entity_name": name})
    })
        .done(function (data) {
            success_callback(data.entity_id);
        })
        .always(function () {
            employee_update_table();
        });
}

function employee_delete_one(entity_id) {
    $.ajax({
        url: '/api/v1/entity/' + entity_id,
        type: 'DELETE',
        contentType: 'application/json;charset=UTF-8',
    }).always(function () {
        employee_update_table();
    });
}

function employee_add_requirements(entity_id, requirement_to_add) {
    for (item of requirement_to_add) {
        $.ajax({
            url: '/api/v1/entity/' + entity_id + '/requirement',
            type: 'POST',
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify(item)
        });
    }
}

function employee_delete_requirement(requirement_id) {
    $.ajax({
        url: '/api/v1/entity/requirement/' + requirement_id,
        type: 'DELETE',
        contentType: 'application/json;charset=UTF-8',
    });
}

function employee_update_location(entity_id, selected_values, original_values) {

    for (let selected of selected_values) {
        if (!original_values.has(selected)) {
            //If selected not in original, that means we need to put it.
            $.ajax({
                url: '/api/v1/location/' + selected + '/entity/' + entity_id,
                type: 'PUT',
                contentType: 'application/json;charset=UTF-8',
            });
        }
    }

    for (let original of original_values) {
        if (!selected_values.has(original)) {
            //If original not in selected, that means we need to delete it.
            $.ajax({
                url: '/api/v1/location/' + original + '/entity/' + entity_id,
                type: 'DELETE',
                contentType: 'application/json;charset=UTF-8',
            });
        }
    }
}

function employee_update_name(entity_id, new_name) {
    $.ajax({
        url: '/api/v1/entity/' + entity_id,
        type: 'PUT',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({"entity_name": new_name})
    }).done(function () {
        employee_update_table();
    });
}

function employee_refresh_requirements_list(element, requirements_list, onlick) {
    let output = "";

    requirements_list.forEach(function (data, index) {

        if (data.state !== employee_REQUIREMENT_DELETE) {
            output += '<tr><td>' + data.data.label + '</td><td><button class="btn btn-primary fake-requirement-class"  data-requirement-index="' + index + '">Edit</button></td></tr>';
        }
    });

    requirements_list.find(".fake-requirement-class").off('click').on('click', onlick);
}