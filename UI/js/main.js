$('#employee_view').load('../partials/employee_partial.html');
$('#shift_view').load('../partials/shift_partial.html');

jQuery.get("http://127.0.0.1:5000/api/v1/entity", function( data ) {
  var output = "";
  data.entity.forEach(function(employee) {
    output += "<tr><td scope=\"row\">" + employee.entity_name + "</td><td><a href=\"edit_employee.html?id=" + employee.entity_id + "\">Edit</td></tr>";
  });
  document.getElementById("employee_table").innerHTML = output;
});

jQuery.get("http://127.0.0.1:5000/api/v1/location", function( locations ) {
  var output = "";
  locations.location.forEach(function(location) {
    output += "<tr><td>" + location.location_label + "</td>";
    output += "<td scope=\"row\"><div class=\"form-group\"><label for=\"start\">Start Date</label><input type=\"date\" class=\"form-control\" id=\"start\"></div>";
    output += "<div class=\"form-group\"><label for=\"end\">End Date</label><input type=\"date\" class=\"form-control\" id=\"end\"></div></td>";
    output += "<td><a href=\"view_schedule.html?location_id=" + location.location_id + "\">View</td>";
    output += "<td><a onClick=\"export(location.location_id)\">Export</td></tr>";
  });

  document.getElementById("shift_table").innerHTML = output;
});