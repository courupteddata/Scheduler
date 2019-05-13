function employee_load() {
    $('#employee_view').load('../partials/employee_partial.html', function () {

        populate_employee_list();
        setup_employee_modal();
    });
}

function populate_employee_list() {

    jQuery.get("/api/v1/entity", function( data ) {
    var output = "";
    data.entity.forEach(function(employee) {
        output += '<tr><td>' + employee.entity_id + '</td><td>' + employee.entity_name + '</td><td><button data-purpose="Edit" data-entity-id="' + employee.entity_id + '" data-entity-name="' + employee.name + '" >Edit</button></td></tr>';
    });
    document.getElementById("employee_table_body").innerHTML = output;
  });
}

function setup_employee_modal() {
    $('#employee_modal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var purpose = button.data('purpose');
        var entity_id = button.data('entityId'); // Extract info from data-* attributes
        var entity_name = button.data("entityName");

        var modal = $(this);

        modal.find('#employee_modal_label').text(purpose + ' Employee');

        var modal_entity_id_form = modal.find('#entity_id_field');
        var modal_entity_name_input = modal.find('#entity_name');
        var modal_delete = modal.find('#employee_delete');

        if (purpose === "Edit") {
            modal_delete.show();

            modal_entity_id_form.show();
            modal_entity_id_form.find('#entity_id').val(entity_id);

            modal_entity_name_input.val(entity_name);

            modal.find('#employee_submit').off('click').click(function () {
                //update_location(location_id, modal_loc_label_input.val());
            });

            modal_delete.off('click').click( function() {
                /delete_location(location_id);
            });

        } else {
            modal_delete.hide();

            modal_entity_id_form.hide();
            modal.find('#employee_submit').off('click').click(function () {
                /create_location(modal_loc_label_input.val());
            });
            //modal_loc_label_input.val("");
        }

    })
}
