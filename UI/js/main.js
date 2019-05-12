document.addEventListener('DOMContentLoaded', function() {

$('#employee_view').load('../partials/employee_partial.html', function(){

    jQuery.get("http://127.0.0.1:5000/api/v1/entity", function( data ) {
    var output = "";
    data.entity.forEach(function(employee) {
      output += "<tr><td scope=\"row\">" + employee.entity_name + "</td><td><a href=\"edit_employee.html?id=" + employee.entity_id + "\">Edit</td></tr>";
    });
    document.getElementById("employee_table_body").innerHTML = output;
  });
});

location_load();
stats_load();

});