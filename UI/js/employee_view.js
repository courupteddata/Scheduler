function employee_load() {
    $('#employee_view').load('../partials/employee_partial.html', function () {

        populate_employee_list()

    });
}

function populate_employee_list() {

    jQuery.get("/api/v1/entity", function( data ) {
    var output = "";
    data.entity.forEach(function(employee) {
        output += '<tr><td>' + employee.entity_id + '</td><td>' + employee.entity_name + '</td><td><button>BlahBlah</button></td></tr>';
    });
    document.getElementById("employee_table_body").innerHTML = output;
  });
}