function stats_load() {
    $('#stats_view').load('../partials/stats_partial.html', function () {

        populate_employee_list()

    });
}

function populate_employee_list() {

    jQuery.get("api/v1/entity", function (entities) {

        var output = "";

        entities.entity.forEach(function (entity) {
            output += '<option data-tokens="' + entity.entity_name + '" data-entity-id="' + entity.entity_id + '">' + entity.entity_name + '</option>';
        });

        document.getElementById("stats_employee_select").innerHTML = output;
    });
}

